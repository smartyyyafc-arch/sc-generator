#!/usr/bin/env node

/**
 * Test Suite Runner - One-Click Execution
 * SC-Generator: Web-based VBS Encryption Tool
 *
 * Execute with: node test-runner.js [options]
 *
 * Options:
 *   --suite=<name>      Run specific test suite
 *   --verbose           Enable verbose output
 *   --quiet             Disable output (except summary)
 *   --timeout=<ms>      Set test timeout (default: 30000)
 *   --report=<file>     Set report output file
 *   --json              Output results as JSON
 *   --parallel          Run tests in parallel
 *   --coverage          Generate coverage report
 */

const fs = require('fs');
const path = require('path');
const { TestFramework, UserSimulator, TestReporter } = require('./test-suite');

// Parse command-line arguments
function parseArgs(argv) {
  const args = {
    suite: null,
    verbose: true,
    quiet: false,
    timeout: 30000,
    report: './test-suite-report.json',
    json: false,
    parallel: false,
    coverage: false,
  };

  for (let i = 2; i < argv.length; i++) {
    const arg = argv[i];

    if (arg.startsWith('--')) {
      const [key, value] = arg.substring(2).split('=');

      if (key === 'suite' && value) args.suite = value;
      if (key === 'verbose') args.verbose = true;
      if (key === 'quiet') {
        args.quiet = true;
        args.verbose = false;
      }
      if (key === 'timeout' && value) args.timeout = parseInt(value, 10);
      if (key === 'report' && value) args.report = value;
      if (key === 'json') args.json = true;
      if (key === 'parallel') args.parallel = true;
      if (key === 'coverage') args.coverage = true;
    }
  }

  return args;
}

// Color output helpers
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  dim: '\x1b[2m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
};

function colorize(text, color) {
  return `${colors[color]}${text}${colors.reset}`;
}

// Test progress indicator
class ProgressBar {
  constructor(total) {
    this.total = total;
    this.current = 0;
    this.startTime = Date.now();
  }

  increment() {
    this.current++;
    this.render();
  }

  render() {
    const percent = (this.current / this.total) * 100;
    const filled = Math.floor((this.current / this.total) * 50);
    const bar = '█'.repeat(filled) + '░'.repeat(50 - filled);
    const elapsed = Date.now() - this.startTime;
    const rate = this.current / (elapsed / 1000);
    const remaining = ((this.total - this.current) / rate) * 1000;

    process.stdout.write(`\r[${bar}] ${percent.toFixed(1)}% (${this.current}/${this.total}) - ${remaining.toFixed(0)}ms remaining`);
  }

  complete() {
    this.current = this.total;
    this.render();
    console.log();
  }
}

// Shared test instance across modules
let sharedTest = null;

function getTestFramework() {
  if (!sharedTest) {
    sharedTest = new TestFramework({
      verbose: true,
      timeout: 30000,
    });
  }
  return sharedTest;
}

// Enhanced test framework with runner features
class EnhancedTestRunner {
  constructor(options = {}) {
    this.options = options;
    this.testFramework = new TestFramework({
      verbose: options.verbose !== false,
      timeout: options.timeout || 30000,
      reportFile: options.report,
      parallel: options.parallel,
    });
    this.progressBar = null;
  }

  async runAllTests() {
    console.log(colorize('\n', 'reset'));
    console.log(colorize('╔════════════════════════════════════════════════════════════════════════════════╗', 'blue'));
    console.log(colorize('║           SC-GENERATOR: ONE-CLICK TEST SUITE EXECUTION                        ║', 'blue'));
    console.log(colorize('╚════════════════════════════════════════════════════════════════════════════════╝\n', 'blue'));

    const startTime = Date.now();

    // Initialize test suites
    this.setupTests();

    // Count total tests
    const totalTests = this.testFramework.tests.length;
    this.progressBar = new ProgressBar(totalTests);

    // Run tests
    try {
      await this.testFramework.run();
      this.progressBar.complete();
    } catch (error) {
      console.error(colorize(`\n✗ Test execution failed: ${error.message}`, 'red'));
      process.exit(1);
    }

    const duration = Date.now() - startTime;

    // Generate report
    this.generateReport(duration);

    // Display summary
    this.displaySummary(duration);

    return this.testFramework.results;
  }

  setupTests() {
    // Load test suite - tests are defined in test-suite.js
    // The test-suite.js file uses the test instance exported from this module
    // Tests are auto-registered when test-suite.js is required
  }

  generateReport(totalDuration) {
    const { results } = this.testFramework;
    const reporter = new TestReporter(results);
    const summary = reporter.generateSummary();

    // JSON report
    const report = {
      timestamp: new Date().toISOString(),
      duration: totalDuration,
      ...summary,
      systemInfo: {
        platform: process.platform,
        nodeVersion: process.version,
        memory: process.memoryUsage(),
      },
    };

    if (this.options.report) {
      fs.writeFileSync(this.options.report, JSON.stringify(report, null, 2));
      console.log(`\n${colorize('Report saved to:', 'cyan')} ${this.options.report}`);
    }

    if (this.options.json) {
      console.log('\n' + JSON.stringify(report, null, 2));
    }

    return report;
  }

  displaySummary(totalDuration) {
    const { results } = this.testFramework;
    const { passed, failed, skipped, total } = results;
    const passRate = ((passed / total) * 100).toFixed(1);

    console.log(colorize('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'blue'));
    console.log(colorize('TEST SUMMARY', 'blue'));
    console.log(colorize('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'blue'));

    console.log(`${colorize('Total Tests:', 'cyan')} ${total}`);
    console.log(`${colorize('Passed:', 'green')} ${passed} ${colorize(`(${passRate}%)`, 'green')}`);
    if (failed > 0) {
      console.log(`${colorize('Failed:', 'red')} ${failed}`);
    }
    if (skipped > 0) {
      console.log(`${colorize('Skipped:', 'yellow')} ${skipped}`);
    }
    console.log(`${colorize('Duration:', 'cyan')} ${totalDuration}ms`);

    console.log(colorize('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'blue'));

    // By suite
    if (results.suites.length > 0) {
      console.log(colorize('\nBY TEST SUITE:', 'cyan'));
      results.suites.forEach(suite => {
        const suitePassRate = suite.passed + suite.failed > 0
          ? ((suite.passed / (suite.passed + suite.failed)) * 100).toFixed(1)
          : '0.0';
        const icon = suite.failed === 0 ? '✓' : '✗';
        const color = suite.failed === 0 ? 'green' : 'red';
        console.log(`  ${colorize(icon, color)} ${suite.name}: ${suite.passed}/${suite.passed + suite.failed} (${suitePassRate}%)`);
      });
    }

    console.log();

    // Exit code
    const exitCode = failed > 0 ? 1 : 0;
    if (exitCode === 0) {
      console.log(colorize('✓ All tests passed!', 'green'));
    } else {
      console.log(colorize('✗ Some tests failed!', 'red'));
    }

    process.exit(exitCode);
  }
}

// Main execution
async function main() {
  const args = parseArgs(process.argv);

  // Print banner with options
  if (args.verbose) {
    console.log(colorize('Options:', 'cyan'));
    console.log(`  Suite: ${args.suite || 'All'}`);
    console.log(`  Timeout: ${args.timeout}ms`);
    console.log(`  Report: ${args.report}`);
    console.log(`  JSON Output: ${args.json}`);
    console.log(`  Parallel: ${args.parallel}`);
  }

  // Create test framework with proper options
  sharedTest = new TestFramework({
    verbose: args.verbose !== false,
    timeout: args.timeout || 30000,
    reportFile: args.report,
    parallel: args.parallel,
  });

  // Load tests from test-suite.js - pass the shared test instance
  const testModule = require('./test-suite');

  // If test-suite exports a test instance, use it; otherwise use ours
  const testFramework = testModule.test || sharedTest;

  const runner = new EnhancedTestRunner(args);
  runner.testFramework = testFramework;
  await runner.runAllTests();
}

if (require.main === module) {
  main().catch(error => {
    console.error(colorize(`Fatal error: ${error.message}`, 'red'));
    process.exit(1);
  });
}

module.exports = { EnhancedTestRunner, parseArgs };
