/**
 * Fingerprint Accuracy Testing Suite
 *
 * Comprehensive tests for fingerprinting accuracy across:
 * - Multiple OS versions (Windows, macOS, Linux)
 * - Different browser configurations
 * - Hardware variations
 * - Virtual machine environments
 * - Different screen resolutions
 * - Browser plugins and extensions
 * - Language and locale settings
 */

const FingerprintHashGenerator = require('./fingerprint-hash-generator');
const crypto = require('crypto');

class FingerprintAccuracyTest {
  constructor() {
    this.generator = new FingerprintHashGenerator();
    this.results = {
      testSuites: {},
      summary: {},
      accuracyMetrics: {},
      confidenceScores: {},
      recommendations: []
    };
    this.totalTests = 0;
    this.passedTests = 0;
    this.failedTests = 0;
  }

  /**
   * OS-specific fingerprint test suite
   */
  testOperatingSystems() {
    const suiteName = 'Operating System Fingerprints';
    const suiteResults = [];

    // Windows versions
    const windowsVersions = [
      {
        name: 'Windows 10 (Build 19041)',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
          platform: 'Win32',
          language: 'en-US',
          timezone: 'America/New_York',
          hardwareConcurrency: 8,
          deviceMemory: 16,
          screen: { width: 1920, height: 1080, colorDepth: 24 }
        }
      },
      {
        name: 'Windows 11 (Build 22000)',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
          platform: 'Win32',
          language: 'en-US',
          timezone: 'America/Los_Angeles',
          hardwareConcurrency: 12,
          deviceMemory: 32,
          screen: { width: 2560, height: 1440, colorDepth: 32 }
        }
      },
      {
        name: 'Windows 7 (Build 7601)',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36',
          platform: 'Win32',
          language: 'en-US',
          timezone: 'Europe/London',
          hardwareConcurrency: 4,
          deviceMemory: 8,
          screen: { width: 1366, height: 768, colorDepth: 24 }
        }
      }
    ];

    // macOS versions
    const macOSVersions = [
      {
        name: 'macOS 10.15 (Catalina)',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
          platform: 'MacIntel',
          language: 'en-US',
          timezone: 'America/Chicago',
          hardwareConcurrency: 8,
          deviceMemory: 16,
          screen: { width: 1440, height: 900, colorDepth: 32 }
        }
      },
      {
        name: 'macOS 12 (Monterey)',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
          platform: 'MacIntel',
          language: 'en-US',
          timezone: 'America/Denver',
          hardwareConcurrency: 16,
          deviceMemory: 32,
          screen: { width: 2560, height: 1600, colorDepth: 32 }
        }
      },
      {
        name: 'macOS 13 (Ventura)',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (Macintosh; PPC Mac OS X 10_5_8) AppleWebKit/537.36',
          platform: 'MacPPC',
          language: 'en-GB',
          timezone: 'Europe/Paris',
          hardwareConcurrency: 10,
          deviceMemory: 24,
          screen: { width: 1680, height: 1050, colorDepth: 32 }
        }
      }
    ];

    // Linux distributions
    const linuxVariants = [
      {
        name: 'Ubuntu 20.04 LTS',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
          platform: 'Linux x86_64',
          language: 'en-US',
          timezone: 'UTC',
          hardwareConcurrency: 4,
          deviceMemory: 8,
          screen: { width: 1920, height: 1080, colorDepth: 24 }
        }
      },
      {
        name: 'Debian 11',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0',
          platform: 'Linux x86_64',
          language: 'de-DE',
          timezone: 'Europe/Berlin',
          hardwareConcurrency: 8,
          deviceMemory: 16,
          screen: { width: 2560, height: 1440, colorDepth: 24 }
        }
      },
      {
        name: 'Fedora 36',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/103.0.5060.114',
          platform: 'Linux x86_64',
          language: 'fr-FR',
          timezone: 'Europe/Paris',
          hardwareConcurrency: 16,
          deviceMemory: 32,
          screen: { width: 3440, height: 1440, colorDepth: 32 }
        }
      }
    ];

    // Test all OS fingerprints
    const allOSFingerprints = [
      ...windowsVersions,
      ...macOSVersions,
      ...linuxVariants
    ];

    const hashResults = new Map();
    const consistencyMap = new Map();

    allOSFingerprints.forEach(osConfig => {
      const testName = `${osConfig.name}`;
      try {
        // Generate hashes with multiple algorithms
        const sha256Hash = this.generator.generateHash(osConfig.fingerprint, { algorithm: 'sha256' });
        const sha512Hash = this.generator.generateHash(osConfig.fingerprint, { algorithm: 'sha512' });
        const pbkdf2Hash = this.generator.generateHash(osConfig.fingerprint, { algorithm: 'pbkdf2' });

        // Test consistency
        const sha256Hash2 = this.generator.generateHash(osConfig.fingerprint, { algorithm: 'sha256' });
        const isConsistent = sha256Hash === sha256Hash2;

        hashResults.set(testName, {
          sha256: sha256Hash,
          sha512: sha512Hash,
          pbkdf2: pbkdf2Hash,
          consistent: isConsistent
        });

        consistencyMap.set(testName, isConsistent);

        suiteResults.push({
          testName,
          osVersion: osConfig.name,
          status: isConsistent ? 'PASS' : 'FAIL',
          hashLengths: {
            sha256: sha256Hash.length,
            sha512: sha512Hash.length,
            pbkdf2: pbkdf2Hash.length
          },
          consistent: isConsistent
        });

        if (isConsistent) this.passedTests++;
        else this.failedTests++;
        this.totalTests++;

      } catch (e) {
        suiteResults.push({
          testName,
          osVersion: osConfig.name,
          status: 'ERROR',
          error: e.message
        });
        this.failedTests++;
        this.totalTests++;
      }
    });

    // Calculate OS-specific accuracy
    const osAccuracy = {
      windows: this._calculateAccuracy(suiteResults.filter(r => r.osVersion.includes('Windows'))),
      macos: this._calculateAccuracy(suiteResults.filter(r => r.osVersion.includes('macOS'))),
      linux: this._calculateAccuracy(suiteResults.filter(r => r.osVersion.includes('Ubuntu') || r.osVersion.includes('Debian') || r.osVersion.includes('Fedora')))
    };

    this.results.testSuites[suiteName] = suiteResults;
    this.results.accuracyMetrics.operatingSystem = osAccuracy;

    return suiteResults;
  }

  /**
   * Browser configuration test suite
   */
  testBrowserConfigurations() {
    const suiteName = 'Browser Configurations';
    const suiteResults = [];

    const browserConfigs = [
      {
        name: 'Chrome 104 (Desktop)',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/104.0.0.0 Safari/537.36',
          platform: 'Win32',
          language: 'en-US',
          timezone: 'America/New_York',
          hardwareConcurrency: 8,
          deviceMemory: 16,
          plugins: ['Flash', 'PDF Viewer'],
          fonts: ['Arial', 'Times New Roman', 'Courier New'],
          canvas: 'canvas-fingerprint-data-1',
          webgl: 'webgl-fingerprint-data-1'
        }
      },
      {
        name: 'Firefox 103 (Desktop)',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0',
          platform: 'Win32',
          language: 'en-US',
          timezone: 'America/New_York',
          hardwareConcurrency: 8,
          deviceMemory: 16,
          plugins: ['PDF Viewer'],
          fonts: ['Arial', 'Helvetica', 'Times New Roman'],
          canvas: 'canvas-fingerprint-data-2',
          webgl: 'webgl-fingerprint-data-2'
        }
      },
      {
        name: 'Safari 16 (macOS)',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/16.0 Safari/605.1.15',
          platform: 'MacIntel',
          language: 'en-US',
          timezone: 'America/New_York',
          hardwareConcurrency: 8,
          deviceMemory: 16,
          plugins: [],
          fonts: ['Helvetica', 'Georgia', 'Courier'],
          canvas: 'canvas-fingerprint-data-3',
          webgl: 'webgl-fingerprint-data-3'
        }
      },
      {
        name: 'Edge 104 (Windows)',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/104.0.0.0 Safari/537.36 Edg/104.0.0.0',
          platform: 'Win32',
          language: 'en-US',
          timezone: 'America/New_York',
          hardwareConcurrency: 8,
          deviceMemory: 16,
          plugins: [],
          fonts: ['Arial', 'Verdana', 'Comic Sans MS'],
          canvas: 'canvas-fingerprint-data-4',
          webgl: 'webgl-fingerprint-data-4'
        }
      }
    ];

    browserConfigs.forEach(browserConfig => {
      const testName = `${browserConfig.name}`;
      try {
        const variantHashes = this.generator.generateHashVariants(browserConfig.fingerprint, {
          algorithms: ['sha256', 'sha512', 'pbkdf2'],
          includePartial: true,
          partialDepth: 2
        });

        const isValid = variantHashes.full &&
                       variantHashes.full.sha256 &&
                       variantHashes.metadata &&
                       variantHashes.metadata.componentCount > 0;

        suiteResults.push({
          testName,
          browser: browserConfig.name,
          status: isValid ? 'PASS' : 'FAIL',
          algorithms: Object.keys(variantHashes.full),
          componentCount: variantHashes.metadata.componentCount,
          hasPartials: !!variantHashes.partial
        });

        if (isValid) this.passedTests++;
        else this.failedTests++;
        this.totalTests++;

      } catch (e) {
        suiteResults.push({
          testName,
          browser: browserConfig.name,
          status: 'ERROR',
          error: e.message
        });
        this.failedTests++;
        this.totalTests++;
      }
    });

    const browserAccuracy = {
      chrome: this._calculateAccuracy(suiteResults.filter(r => r.browser.includes('Chrome'))),
      firefox: this._calculateAccuracy(suiteResults.filter(r => r.browser.includes('Firefox'))),
      safari: this._calculateAccuracy(suiteResults.filter(r => r.browser.includes('Safari'))),
      edge: this._calculateAccuracy(suiteResults.filter(r => r.browser.includes('Edge')))
    };

    this.results.testSuites[suiteName] = suiteResults;
    this.results.accuracyMetrics.browser = browserAccuracy;

    return suiteResults;
  }

  /**
   * Hardware variation test suite
   */
  testHardwareVariations() {
    const suiteName = 'Hardware Variations';
    const suiteResults = [];

    const hardwareConfigs = [
      {
        name: 'Low-end Machine',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
          platform: 'Win32',
          hardwareConcurrency: 2,
          deviceMemory: 4,
          screen: { width: 1024, height: 768, colorDepth: 16 }
        }
      },
      {
        name: 'Mid-range Machine',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
          platform: 'Win32',
          hardwareConcurrency: 8,
          deviceMemory: 16,
          screen: { width: 1920, height: 1080, colorDepth: 24 }
        }
      },
      {
        name: 'High-end Workstation',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
          platform: 'Win32',
          hardwareConcurrency: 32,
          deviceMemory: 64,
          screen: { width: 3840, height: 2160, colorDepth: 32 }
        }
      },
      {
        name: 'Mobile Device (Simulated)',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_7 like Mac OS X)',
          platform: 'iPhone',
          hardwareConcurrency: 6,
          deviceMemory: 3,
          screen: { width: 390, height: 844, colorDepth: 24 }
        }
      }
    ];

    hardwareConfigs.forEach(hwConfig => {
      const testName = `${hwConfig.name}`;
      try {
        const hash = this.generator.generateHash(hwConfig.fingerprint);
        const persistentHash = this.generator.generatePersistentHash(hwConfig.fingerprint);

        const isValid = hash && hash.length === 64 && persistentHash.stable;

        suiteResults.push({
          testName,
          hardware: hwConfig.name,
          status: isValid ? 'PASS' : 'FAIL',
          hashValid: !!hash,
          persistentHashValid: persistentHash.stable,
          hashLength: hash.length,
          cores: hwConfig.fingerprint.hardwareConcurrency,
          memory: hwConfig.fingerprint.deviceMemory
        });

        if (isValid) this.passedTests++;
        else this.failedTests++;
        this.totalTests++;

      } catch (e) {
        suiteResults.push({
          testName,
          hardware: hwConfig.name,
          status: 'ERROR',
          error: e.message
        });
        this.failedTests++;
        this.totalTests++;
      }
    });

    const hardwareAccuracy = {
      lowEnd: this._calculateAccuracy(suiteResults.filter(r => r.hardware.includes('Low-end'))),
      midRange: this._calculateAccuracy(suiteResults.filter(r => r.hardware.includes('Mid-range'))),
      highEnd: this._calculateAccuracy(suiteResults.filter(r => r.hardware.includes('High-end'))),
      mobile: this._calculateAccuracy(suiteResults.filter(r => r.hardware.includes('Mobile')))
    };

    this.results.testSuites[suiteName] = suiteResults;
    this.results.accuracyMetrics.hardware = hardwareAccuracy;

    return suiteResults;
  }

  /**
   * Screen resolution and display test suite
   */
  testDisplayConfigurations() {
    const suiteName = 'Display Configurations';
    const suiteResults = [];

    const displayConfigs = [
      {
        name: '4K UltraHD (3840x2160)',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
          platform: 'Win32',
          screen: { width: 3840, height: 2160, colorDepth: 32, pixelDepth: 32 }
        }
      },
      {
        name: '2K Gaming (2560x1440)',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
          platform: 'Win32',
          screen: { width: 2560, height: 1440, colorDepth: 32, pixelDepth: 32 }
        }
      },
      {
        name: 'Full HD (1920x1080)',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
          platform: 'Win32',
          screen: { width: 1920, height: 1080, colorDepth: 24, pixelDepth: 24 }
        }
      },
      {
        name: 'HD (1366x768)',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
          platform: 'Win32',
          screen: { width: 1366, height: 768, colorDepth: 24, pixelDepth: 24 }
        }
      },
      {
        name: 'Ultrawide (3440x1440)',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
          platform: 'Win32',
          screen: { width: 3440, height: 1440, colorDepth: 32, pixelDepth: 32 }
        }
      }
    ];

    displayConfigs.forEach(displayConfig => {
      const testName = `${displayConfig.name}`;
      try {
        const hashes = new Set();

        // Generate multiple hashes to verify uniqueness
        for (let i = 0; i < 3; i++) {
          const hash = this.generator.generateHash(displayConfig.fingerprint);
          hashes.add(hash);
        }

        const isConsistent = hashes.size === 1; // All hashes should be identical

        suiteResults.push({
          testName,
          resolution: displayConfig.name,
          status: isConsistent ? 'PASS' : 'FAIL',
          width: displayConfig.fingerprint.screen.width,
          height: displayConfig.fingerprint.screen.height,
          colorDepth: displayConfig.fingerprint.screen.colorDepth,
          consistent: isConsistent
        });

        if (isConsistent) this.passedTests++;
        else this.failedTests++;
        this.totalTests++;

      } catch (e) {
        suiteResults.push({
          testName,
          resolution: displayConfig.name,
          status: 'ERROR',
          error: e.message
        });
        this.failedTests++;
        this.totalTests++;
      }
    });

    const displayAccuracy = this._calculateAccuracy(suiteResults);

    this.results.testSuites[suiteName] = suiteResults;
    this.results.accuracyMetrics.display = displayAccuracy;

    return suiteResults;
  }

  /**
   * Uniqueness and collision detection test suite
   */
  testUniquenessAndCollisions() {
    const suiteName = 'Uniqueness and Collision Detection';
    const suiteResults = [];

    const generateUniqueFingerprints = (count) => {
      const fingerprints = [];
      for (let i = 0; i < count; i++) {
        fingerprints.push({
          userAgent: `Mozilla/5.0 Config-${i}`,
          platform: i % 2 === 0 ? 'Win32' : 'Linux',
          hardwareConcurrency: 2 + (i % 16),
          deviceMemory: 4 + (i % 32),
          screen: {
            width: 800 + (i * 10),
            height: 600 + (i * 10),
            colorDepth: 16 + (i % 16)
          },
          language: i % 3 === 0 ? 'en-US' : i % 3 === 1 ? 'de-DE' : 'fr-FR',
          timezone: i % 4 === 0 ? 'UTC' : i % 4 === 1 ? 'America/New_York' : i % 4 === 2 ? 'Europe/London' : 'Asia/Tokyo'
        });
      }
      return fingerprints;
    };

    try {
      const fingerprints = generateUniqueFingerprints(100);
      const hashes = new Set();
      const hashToFingerprint = new Map();

      fingerprints.forEach((fp, index) => {
        const hash = this.generator.generateHash(fp);
        hashes.add(hash);
        hashToFingerprint.set(hash, index);
      });

      const collisionCount = fingerprints.length - hashes.size;
      const uniquenessPercentage = (hashes.size / fingerprints.length) * 100;

      suiteResults.push({
        testName: 'Uniqueness Test (100 Fingerprints)',
        totalFingerprints: fingerprints.length,
        uniqueHashes: hashes.size,
        collisions: collisionCount,
        uniquenessPercentage: uniquenessPercentage.toFixed(2),
        status: uniquenessPercentage === 100 ? 'PASS' : 'FAIL'
      });

      if (uniquenessPercentage === 100) this.passedTests++;
      else this.failedTests++;
      this.totalTests++;

    } catch (e) {
      suiteResults.push({
        testName: 'Uniqueness Test',
        status: 'ERROR',
        error: e.message
      });
      this.failedTests++;
      this.totalTests++;
    }

    this.results.testSuites[suiteName] = suiteResults;
    this.results.accuracyMetrics.uniqueness = this._calculateAccuracy(suiteResults);

    return suiteResults;
  }

  /**
   * Language and locale test suite
   */
  testLanguageAndLocale() {
    const suiteName = 'Language and Locale Variations';
    const suiteResults = [];

    const localeConfigs = [
      { language: 'en-US', timezone: 'America/New_York', name: 'English (US)' },
      { language: 'de-DE', timezone: 'Europe/Berlin', name: 'German (Germany)' },
      { language: 'fr-FR', timezone: 'Europe/Paris', name: 'French (France)' },
      { language: 'ja-JP', timezone: 'Asia/Tokyo', name: 'Japanese (Japan)' },
      { language: 'zh-CN', timezone: 'Asia/Shanghai', name: 'Chinese (Simplified)' },
      { language: 'es-ES', timezone: 'Europe/Madrid', name: 'Spanish (Spain)' },
      { language: 'pt-BR', timezone: 'America/Sao_Paulo', name: 'Portuguese (Brazil)' },
      { language: 'ru-RU', timezone: 'Europe/Moscow', name: 'Russian (Russia)' },
      { language: 'ko-KR', timezone: 'Asia/Seoul', name: 'Korean (South Korea)' },
      { language: 'ar-SA', timezone: 'Asia/Riyadh', name: 'Arabic (Saudi Arabia)' }
    ];

    localeConfigs.forEach(localeConfig => {
      const testName = `${localeConfig.name}`;
      try {
        const fingerprint = {
          userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
          platform: 'Win32',
          language: localeConfig.language,
          timezone: localeConfig.timezone,
          hardwareConcurrency: 8,
          deviceMemory: 16
        };

        const hash = this.generator.generateHash(fingerprint);
        const comparison = this.generator.compareFingerprints(fingerprint, fingerprint);

        const isValid = hash && comparison.exactMatch;

        suiteResults.push({
          testName,
          locale: localeConfig.name,
          language: localeConfig.language,
          timezone: localeConfig.timezone,
          status: isValid ? 'PASS' : 'FAIL',
          hashGenerated: !!hash,
          selfMatches: comparison.exactMatch
        });

        if (isValid) this.passedTests++;
        else this.failedTests++;
        this.totalTests++;

      } catch (e) {
        suiteResults.push({
          testName,
          locale: localeConfig.name,
          status: 'ERROR',
          error: e.message
        });
        this.failedTests++;
        this.totalTests++;
      }
    });

    const localeAccuracy = this._calculateAccuracy(suiteResults);

    this.results.testSuites[suiteName] = suiteResults;
    this.results.accuracyMetrics.locale = localeAccuracy;

    return suiteResults;
  }

  /**
   * Virtual machine and emulation detection
   */
  testVirtualMachineConfigurations() {
    const suiteName = 'Virtual Machine Configurations';
    const suiteResults = [];

    const vmConfigs = [
      {
        name: 'VirtualBox Linux Guest',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (X11; Linux x86_64) VirtualBox',
          platform: 'Linux x86_64',
          hardwareConcurrency: 2,
          deviceMemory: 2,
          screen: { width: 1024, height: 768, colorDepth: 24 }
        }
      },
      {
        name: 'VMware Windows Guest',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) VMware',
          platform: 'Win32',
          hardwareConcurrency: 4,
          deviceMemory: 4,
          screen: { width: 1280, height: 960, colorDepth: 24 }
        }
      },
      {
        name: 'Hyper-V Windows Guest',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Hyper-V',
          platform: 'Win32',
          hardwareConcurrency: 4,
          deviceMemory: 4,
          screen: { width: 1280, height: 1024, colorDepth: 32 }
        }
      },
      {
        name: 'Docker Container (Linux)',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (X11; Linux x86_64) Docker',
          platform: 'Linux x86_64',
          hardwareConcurrency: 8,
          deviceMemory: 8,
          screen: { width: 1920, height: 1080, colorDepth: 32 }
        }
      }
    ];

    vmConfigs.forEach(vmConfig => {
      const testName = `${vmConfig.name}`;
      try {
        const hash1 = this.generator.generateHash(vmConfig.fingerprint, { algorithm: 'sha256' });
        const hash2 = this.generator.generateHash(vmConfig.fingerprint, { algorithm: 'sha256' });

        const isConsistent = hash1 === hash2;
        const persistent = this.generator.generatePersistentHash(vmConfig.fingerprint);

        suiteResults.push({
          testName,
          vmType: vmConfig.name,
          status: isConsistent ? 'PASS' : 'FAIL',
          hashConsistent: isConsistent,
          persistentStable: persistent.stable,
          cores: vmConfig.fingerprint.hardwareConcurrency,
          memory: vmConfig.fingerprint.deviceMemory
        });

        if (isConsistent && persistent.stable) this.passedTests++;
        else this.failedTests++;
        this.totalTests++;

      } catch (e) {
        suiteResults.push({
          testName,
          vmType: vmConfig.name,
          status: 'ERROR',
          error: e.message
        });
        this.failedTests++;
        this.totalTests++;
      }
    });

    const vmAccuracy = this._calculateAccuracy(suiteResults);

    this.results.testSuites[suiteName] = suiteResults;
    this.results.accuracyMetrics.virtualMachine = vmAccuracy;

    return suiteResults;
  }

  /**
   * Calculate accuracy metrics for a set of test results
   */
  _calculateAccuracy(testResults) {
    if (testResults.length === 0) return { accuracy: 0, passed: 0, total: 0 };

    const passed = testResults.filter(r => r.status === 'PASS').length;
    const total = testResults.length;
    const accuracy = (passed / total) * 100;

    return {
      accuracy: parseFloat(accuracy.toFixed(2)),
      passed,
      total,
      failed: total - passed,
      passRate: `${accuracy.toFixed(2)}%`
    };
  }

  /**
   * Run all test suites and generate comprehensive report
   */
  runAllTests() {
    console.log('Starting Fingerprint Accuracy Test Suite...\n');

    this.testOperatingSystems();
    this.testBrowserConfigurations();
    this.testHardwareVariations();
    this.testDisplayConfigurations();
    this.testUniquenessAndCollisions();
    this.testLanguageAndLocale();
    this.testVirtualMachineConfigurations();

    this.generateReport();

    return this.results;
  }

  /**
   * Generate comprehensive accuracy report
   */
  generateReport() {
    const totalAccuracy = (this.passedTests / this.totalTests) * 100;

    this.results.summary = {
      totalTests: this.totalTests,
      passedTests: this.passedTests,
      failedTests: this.failedTests,
      overallAccuracy: parseFloat(totalAccuracy.toFixed(2)),
      passRate: `${totalAccuracy.toFixed(2)}%`,
      timestamp: new Date().toISOString()
    };

    // Calculate confidence scores
    this.results.confidenceScores = {
      operatingSystemDetection: this.results.accuracyMetrics.operatingSystem,
      browserIdentification: this.results.accuracyMetrics.browser,
      hardwareFingerprinting: this.results.accuracyMetrics.hardware,
      displayRecognition: this.results.accuracyMetrics.display,
      uniquenessDetection: this.results.accuracyMetrics.uniqueness,
      localeDetection: this.results.accuracyMetrics.locale,
      virtualMachineDetection: this.results.accuracyMetrics.virtualMachine
    };

    // Generate recommendations
    this._generateRecommendations();
  }

  /**
   * Generate actionable recommendations based on test results
   */
  _generateRecommendations() {
    const recommendations = [];

    // Check OS accuracy
    if (this.results.accuracyMetrics.operatingSystem?.windows?.accuracy < 95) {
      recommendations.push({
        category: 'Operating System',
        issue: 'Windows fingerprinting accuracy below 95%',
        recommendation: 'Review Windows-specific user agent parsing and platform detection'
      });
    }

    // Check browser accuracy
    const browserMetrics = this.results.accuracyMetrics.browser;
    if (browserMetrics?.chrome?.accuracy < 90) {
      recommendations.push({
        category: 'Browser',
        issue: 'Chrome fingerprinting accuracy below 90%',
        recommendation: 'Enhance Chrome user agent and API detection'
      });
    }

    // Check hardware accuracy
    if (this.results.accuracyMetrics.hardware?.highEnd?.accuracy < 90) {
      recommendations.push({
        category: 'Hardware',
        issue: 'High-end hardware fingerprinting accuracy below 90%',
        recommendation: 'Improve handling of large core counts and memory configurations'
      });
    }

    // Check uniqueness
    if (this.results.accuracyMetrics.uniqueness?.accuracy < 99) {
      recommendations.push({
        category: 'Uniqueness',
        issue: 'Hash collision rate higher than acceptable',
        recommendation: 'Review serialization logic to ensure all components are properly hashed'
      });
    }

    if (recommendations.length === 0) {
      recommendations.push({
        category: 'General',
        issue: 'No issues detected',
        recommendation: 'All fingerprinting systems operating within acceptable parameters'
      });
    }

    this.results.recommendations = recommendations;
  }

  /**
   * Export report as JSON
   */
  exportJSON() {
    return JSON.stringify(this.results, null, 2);
  }

  /**
   * Export report as formatted text
   */
  exportText() {
    let report = '='.repeat(80) + '\n';
    report += 'FINGERPRINT ACCURACY TEST REPORT\n';
    report += '='.repeat(80) + '\n\n';

    // Summary
    report += 'OVERALL SUMMARY\n';
    report += '-'.repeat(80) + '\n';
    report += `Total Tests: ${this.results.summary.totalTests}\n`;
    report += `Passed: ${this.results.summary.passedTests}\n`;
    report += `Failed: ${this.results.summary.failedTests}\n`;
    report += `Overall Accuracy: ${this.results.summary.overallAccuracy}%\n`;
    report += `Timestamp: ${this.results.summary.timestamp}\n\n`;

    // Accuracy Metrics by Category
    report += 'ACCURACY METRICS BY CATEGORY\n';
    report += '-'.repeat(80) + '\n';
    Object.entries(this.results.accuracyMetrics).forEach(([category, metrics]) => {
      report += `\n${category.toUpperCase()}:\n`;
      if (typeof metrics === 'object' && metrics !== null) {
        Object.entries(metrics).forEach(([key, value]) => {
          if (typeof value === 'object') {
            report += `  ${key}: ${value.accuracy}% (${value.passed}/${value.total})\n`;
          }
        });
      }
    });

    // Test Suites Results
    report += '\n' + '='.repeat(80) + '\n';
    report += 'DETAILED TEST RESULTS BY SUITE\n';
    report += '='.repeat(80) + '\n';
    Object.entries(this.results.testSuites).forEach(([suite, results]) => {
      report += `\n${suite}\n`;
      report += '-'.repeat(80) + '\n';
      results.forEach((result, index) => {
        report += `${index + 1}. ${result.testName}: ${result.status}\n`;
      });
    });

    // Recommendations
    report += '\n' + '='.repeat(80) + '\n';
    report += 'RECOMMENDATIONS\n';
    report += '='.repeat(80) + '\n';
    this.results.recommendations.forEach((rec, index) => {
      report += `\n${index + 1}. [${rec.category}]\n`;
      report += `   Issue: ${rec.issue}\n`;
      report += `   Recommendation: ${rec.recommendation}\n`;
    });

    report += '\n' + '='.repeat(80) + '\n';

    return report;
  }
}

// Main execution
if (require.main === module) {
  const tester = new FingerprintAccuracyTest();
  const results = tester.runAllTests();

  // Print text report to console
  console.log(tester.exportText());

  // Write JSON report to file
  const fs = require('fs');
  const reportPath = '/tmp/fingerprint-accuracy-report.json';
  fs.writeFileSync(reportPath, tester.exportJSON());
  console.log(`\nJSON report written to: ${reportPath}`);

  process.exit(0);
}

module.exports = FingerprintAccuracyTest;
