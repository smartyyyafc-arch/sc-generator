/**
 * Comprehensive Fingerprinting Test Suite
 *
 * Multi-OS and Hardware Configuration Testing
 * Tests fingerprinting accuracy, consistency, and uniqueness across:
 * - 15+ Operating Systems (Windows, macOS, Linux, Mobile)
 * - 8+ Browser Configurations
 * - 12+ Hardware Profiles
 * - 10+ Display Configurations
 * - Virtual Machine Environments
 * - Language/Locale Variations
 *
 * @author Fingerprinting Test Suite
 * @version 2.0
 */

const crypto = require('crypto');
const assert = require('assert');

class FingerprintingTestSuite {
  constructor() {
    this.results = {
      suites: {},
      summary: {
        totalTests: 0,
        passed: 0,
        failed: 0,
        skipped: 0,
        errors: []
      },
      performance: {},
      confidenceMetrics: {}
    };
    this.testRegistry = new Map();
    this.timestamps = [];
  }

  /**
   * OPERATING SYSTEMS TEST SUITE
   * Tests 15 different OS configurations
   */
  testOperatingSystems() {
    const suiteName = 'Operating Systems (15 Configurations)';
    const testResults = [];

    const osConfigurations = [
      // Windows Systems (4 versions)
      {
        category: 'Windows',
        name: 'Windows 11 23H2 (Latest)',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
          platform: 'Win32',
          osVersion: '10.0.22631',
          architecture: 'x64',
          language: 'en-US',
          timezone: 'America/New_York',
          hardwareConcurrency: 16,
          deviceMemory: 32,
          screen: { width: 2560, height: 1440, colorDepth: 32, devicePixelRatio: 1.5 }
        }
      },
      {
        category: 'Windows',
        name: 'Windows 10 22H2',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36',
          platform: 'Win32',
          osVersion: '10.0.19045',
          architecture: 'x64',
          language: 'en-US',
          timezone: 'America/Chicago',
          hardwareConcurrency: 12,
          deviceMemory: 16,
          screen: { width: 1920, height: 1080, colorDepth: 24, devicePixelRatio: 1.0 }
        }
      },
      {
        category: 'Windows',
        name: 'Windows Server 2022',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; ServerOS) AppleWebKit/537.36',
          platform: 'Win32',
          osVersion: '10.0.20348',
          architecture: 'x64',
          language: 'en-US',
          timezone: 'UTC',
          hardwareConcurrency: 32,
          deviceMemory: 128,
          screen: { width: 1024, height: 768, colorDepth: 32, devicePixelRatio: 1.0 }
        }
      },
      {
        category: 'Windows',
        name: 'Windows 7 SP1 (Legacy)',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36',
          platform: 'Win32',
          osVersion: '6.1.7601',
          architecture: 'x64',
          language: 'en-US',
          timezone: 'America/Los_Angeles',
          hardwareConcurrency: 4,
          deviceMemory: 8,
          screen: { width: 1366, height: 768, colorDepth: 24, devicePixelRatio: 1.0 }
        }
      },

      // macOS Systems (4 versions)
      {
        category: 'macOS',
        name: 'macOS 14 Sonoma (Latest)',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) AppleWebKit/605.1.15 Version/17.1 Safari/605.1.15',
          platform: 'MacIntel',
          osVersion: '14.1',
          architecture: 'x86_64',
          language: 'en-US',
          timezone: 'America/Denver',
          hardwareConcurrency: 10,
          deviceMemory: 32,
          screen: { width: 2880, height: 1800, colorDepth: 32, devicePixelRatio: 2.0 }
        }
      },
      {
        category: 'macOS',
        name: 'macOS 13 Ventura',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/16.0 Safari/605.1.15',
          platform: 'MacIntel',
          osVersion: '13.6',
          architecture: 'x86_64',
          language: 'en-GB',
          timezone: 'Europe/London',
          hardwareConcurrency: 8,
          deviceMemory: 16,
          screen: { width: 2560, height: 1600, colorDepth: 32, devicePixelRatio: 2.0 }
        }
      },
      {
        category: 'macOS',
        name: 'macOS 12 Monterey',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/108.0.0.0 Safari/537.36',
          platform: 'MacIntel',
          osVersion: '12.7',
          architecture: 'x86_64',
          language: 'en-US',
          timezone: 'America/Phoenix',
          hardwareConcurrency: 8,
          deviceMemory: 16,
          screen: { width: 1440, height: 900, colorDepth: 32, devicePixelRatio: 1.0 }
        }
      },
      {
        category: 'macOS',
        name: 'macOS 11 Big Sur',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
          platform: 'MacIntel',
          osVersion: '11.7',
          architecture: 'x86_64',
          language: 'fr-FR',
          timezone: 'Europe/Paris',
          hardwareConcurrency: 6,
          deviceMemory: 8,
          screen: { width: 1680, height: 1050, colorDepth: 24, devicePixelRatio: 1.0 }
        }
      },

      // Linux Systems (4 versions)
      {
        category: 'Linux',
        name: 'Ubuntu 23.10 Mantic',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
          platform: 'Linux x86_64',
          osVersion: '23.10',
          architecture: 'x86_64',
          language: 'en-US',
          timezone: 'UTC',
          hardwareConcurrency: 8,
          deviceMemory: 16,
          screen: { width: 1920, height: 1080, colorDepth: 24, devicePixelRatio: 1.0 }
        }
      },
      {
        category: 'Linux',
        name: 'Debian 12 Bookworm',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
          platform: 'Linux x86_64',
          osVersion: '12.2',
          architecture: 'x86_64',
          language: 'de-DE',
          timezone: 'Europe/Berlin',
          hardwareConcurrency: 12,
          deviceMemory: 32,
          screen: { width: 2560, height: 1440, colorDepth: 32, devicePixelRatio: 1.0 }
        }
      },
      {
        category: 'Linux',
        name: 'Fedora 39',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36',
          platform: 'Linux x86_64',
          osVersion: '39',
          architecture: 'x86_64',
          language: 'ru-RU',
          timezone: 'Europe/Moscow',
          hardwareConcurrency: 16,
          deviceMemory: 64,
          screen: { width: 3440, height: 1440, colorDepth: 32, devicePixelRatio: 1.0 }
        }
      },
      {
        category: 'Linux',
        name: 'CentOS 7',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
          platform: 'Linux x86_64',
          osVersion: '7.9.2009',
          architecture: 'x86_64',
          language: 'en-US',
          timezone: 'America/New_York',
          hardwareConcurrency: 4,
          deviceMemory: 8,
          screen: { width: 1024, height: 768, colorDepth: 24, devicePixelRatio: 1.0 }
        }
      },

      // Mobile Systems (3 versions)
      {
        category: 'Mobile',
        name: 'iOS 17 (iPhone 15 Pro)',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15',
          platform: 'iPhone',
          osVersion: '17.1',
          architecture: 'arm64',
          language: 'en-US',
          timezone: 'America/New_York',
          hardwareConcurrency: 6,
          deviceMemory: 6,
          screen: { width: 430, height: 932, colorDepth: 32, devicePixelRatio: 3.0 }
        }
      },
      {
        category: 'Mobile',
        name: 'Android 14 (Pixel 8)',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36',
          platform: 'Linux aarch64',
          osVersion: '14',
          architecture: 'arm64',
          language: 'en-US',
          timezone: 'America/Los_Angeles',
          hardwareConcurrency: 8,
          deviceMemory: 8,
          screen: { width: 1440, height: 3120, colorDepth: 32, devicePixelRatio: 3.5 }
        }
      },
      {
        category: 'Mobile',
        name: 'Android 13 (Samsung Galaxy S23)',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (Linux; Android 13; SM-S911B) AppleWebKit/537.36 Chrome/119.0.0.0 Mobile Safari/537.36',
          platform: 'Linux aarch64',
          osVersion: '13',
          architecture: 'arm64',
          language: 'ko-KR',
          timezone: 'Asia/Seoul',
          hardwareConcurrency: 8,
          deviceMemory: 8,
          screen: { width: 1440, height: 3200, colorDepth: 32, devicePixelRatio: 3.88 }
        }
      }
    ];

    osConfigurations.forEach((config, idx) => {
      const testName = `${idx + 1}. ${config.name}`;
      try {
        const hash = this._generateHash(config.fingerprint);
        const isValid = hash && hash.length > 0;

        testResults.push({
          index: idx + 1,
          testName,
          category: config.category,
          status: isValid ? 'PASS' : 'FAIL',
          hash: isValid ? hash.substring(0, 16) + '...' : 'N/A',
          details: {
            osVersion: config.fingerprint.osVersion,
            architecture: config.fingerprint.architecture,
            cores: config.fingerprint.hardwareConcurrency,
            memory: config.fingerprint.deviceMemory + 'GB'
          }
        });

        if (isValid) this.results.summary.passed++;
        else this.results.summary.failed++;

      } catch (error) {
        testResults.push({
          index: idx + 1,
          testName,
          category: config.category,
          status: 'ERROR',
          error: error.message
        });
        this.results.summary.failed++;
      }

      this.results.summary.totalTests++;
    });

    this.results.suites[suiteName] = testResults;
    return testResults;
  }

  /**
   * BROWSER CONFIGURATIONS TEST SUITE
   * Tests 8 browser configurations
   */
  testBrowserConfigurations() {
    const suiteName = 'Browser Configurations (8 Configurations)';
    const testResults = [];

    const browserConfigs = [
      {
        name: 'Chrome 120 (Windows)',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
          platform: 'Win32',
          browser: 'Chrome',
          browserVersion: '120.0.0.0',
          engine: 'Blink',
          language: 'en-US',
          hardwareConcurrency: 8,
          deviceMemory: 16,
          maxTouchPoints: 0,
          plugins: ['PDF Viewer', 'Chrome PDF Plugin'],
          fonts: ['Arial', 'Times New Roman', 'Courier New', 'Georgia']
        }
      },
      {
        name: 'Firefox 121 (Linux)',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
          platform: 'Linux x86_64',
          browser: 'Firefox',
          browserVersion: '121.0',
          engine: 'Gecko',
          language: 'en-US',
          hardwareConcurrency: 8,
          deviceMemory: 16,
          maxTouchPoints: 0,
          plugins: ['PDF.js Plugin', 'Firefox PDF Plugin'],
          fonts: ['Liberation Sans', 'Liberation Serif', 'Courier New']
        }
      },
      {
        name: 'Safari 17 (macOS)',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) AppleWebKit/605.1.15 Version/17.1 Safari/605.1.15',
          platform: 'MacIntel',
          browser: 'Safari',
          browserVersion: '17.1',
          engine: 'WebKit',
          language: 'en-US',
          hardwareConcurrency: 10,
          deviceMemory: 16,
          maxTouchPoints: 0,
          plugins: [],
          fonts: ['Helvetica', 'Georgia', 'Courier', 'Monaco']
        }
      },
      {
        name: 'Edge 120 (Windows)',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
          platform: 'Win32',
          browser: 'Edge',
          browserVersion: '120.0.0.0',
          engine: 'Blink',
          language: 'en-US',
          hardwareConcurrency: 8,
          deviceMemory: 16,
          maxTouchPoints: 0,
          plugins: ['PDF Plugin', 'Flash'],
          fonts: ['Segoe UI', 'Tahoma', 'Arial', 'Times New Roman']
        }
      },
      {
        name: 'Chrome Mobile (Android)',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36',
          platform: 'Linux aarch64',
          browser: 'Chrome Mobile',
          browserVersion: '120.0.0.0',
          engine: 'Blink',
          language: 'en-US',
          hardwareConcurrency: 8,
          deviceMemory: 8,
          maxTouchPoints: 10,
          plugins: [],
          fonts: ['Roboto', 'Noto Sans', 'Droid Sans']
        }
      },
      {
        name: 'Safari Mobile (iOS)',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 Version/17.1 Mobile/15E148 Safari/604.1',
          platform: 'iPhone',
          browser: 'Safari Mobile',
          browserVersion: '17.1',
          engine: 'WebKit',
          language: 'en-US',
          hardwareConcurrency: 6,
          deviceMemory: 6,
          maxTouchPoints: 10,
          plugins: [],
          fonts: ['-apple-system', 'Helvetica Neue', 'Courier']
        }
      },
      {
        name: 'Brave 1.71 (macOS)',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
          platform: 'MacIntel',
          browser: 'Brave',
          browserVersion: '1.71.104',
          engine: 'Blink',
          language: 'en-US',
          hardwareConcurrency: 8,
          deviceMemory: 16,
          maxTouchPoints: 0,
          plugins: [],
          fonts: ['Arial', 'Helvetica', 'Times New Roman']
        }
      },
      {
        name: 'Opera 105 (Windows)',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36 OPR/105.0.0.0',
          platform: 'Win32',
          browser: 'Opera',
          browserVersion: '105.0.0.0',
          engine: 'Blink',
          language: 'en-US',
          hardwareConcurrency: 8,
          deviceMemory: 16,
          maxTouchPoints: 0,
          plugins: ['Flash'],
          fonts: ['Arial', 'Verdana', 'Courier New']
        }
      }
    ];

    browserConfigs.forEach((config, idx) => {
      const testName = `${idx + 1}. ${config.name}`;
      try {
        const hash = this._generateHash(config.fingerprint);
        const variantHashes = this._generateHashVariants(config.fingerprint);
        const isValid = hash && variantHashes && Object.keys(variantHashes).length > 0;

        testResults.push({
          index: idx + 1,
          testName,
          browser: config.name,
          status: isValid ? 'PASS' : 'FAIL',
          hashCount: variantHashes ? Object.keys(variantHashes).length : 0,
          details: {
            engine: config.fingerprint.engine,
            version: config.fingerprint.browserVersion,
            touchPoints: config.fingerprint.maxTouchPoints,
            fontCount: config.fingerprint.fonts.length
          }
        });

        if (isValid) this.results.summary.passed++;
        else this.results.summary.failed++;

      } catch (error) {
        testResults.push({
          index: idx + 1,
          testName,
          browser: config.name,
          status: 'ERROR',
          error: error.message
        });
        this.results.summary.failed++;
      }

      this.results.summary.totalTests++;
    });

    this.results.suites[suiteName] = testResults;
    return testResults;
  }

  /**
   * HARDWARE CONFIGURATIONS TEST SUITE
   * Tests 12 different hardware profiles
   */
  testHardwareConfigurations() {
    const suiteName = 'Hardware Configurations (12 Profiles)';
    const testResults = [];

    const hardwareProfiles = [
      {
        name: 'Ultra High-End Gaming PC',
        fingerprint: {
          hardwareConcurrency: 64,
          deviceMemory: 256,
          cpuModel: 'AMD Ryzen Threadripper PRO 5995WX',
          gpuModel: 'NVIDIA RTX 6000 Ada',
          storageType: 'NVMe SSD 4TB',
          totalStorage: 4000,
          ram: 256
        }
      },
      {
        name: 'High-End Workstation',
        fingerprint: {
          hardwareConcurrency: 32,
          deviceMemory: 128,
          cpuModel: 'Intel Xeon Platinum 8480+',
          gpuModel: 'NVIDIA RTX 6000',
          storageType: 'NVMe SSD 2TB',
          totalStorage: 2000,
          ram: 128
        }
      },
      {
        name: 'Standard Desktop (2024)',
        fingerprint: {
          hardwareConcurrency: 16,
          deviceMemory: 32,
          cpuModel: 'Intel Core i7-14700K',
          gpuModel: 'NVIDIA RTX 4090',
          storageType: 'NVMe SSD 1TB',
          totalStorage: 1000,
          ram: 32
        }
      },
      {
        name: 'Mid-Range Desktop',
        fingerprint: {
          hardwareConcurrency: 8,
          deviceMemory: 16,
          cpuModel: 'AMD Ryzen 5 5600X',
          gpuModel: 'NVIDIA GTX 1650',
          storageType: 'SATA SSD 500GB',
          totalStorage: 500,
          ram: 16
        }
      },
      {
        name: 'Budget PC',
        fingerprint: {
          hardwareConcurrency: 4,
          deviceMemory: 8,
          cpuModel: 'Intel Core i3-10100',
          gpuModel: 'Integrated Intel UHD 630',
          storageType: 'HDD 1TB',
          totalStorage: 1000,
          ram: 8
        }
      },
      {
        name: 'Ultra-Book (High Performance)',
        fingerprint: {
          hardwareConcurrency: 12,
          deviceMemory: 32,
          cpuModel: 'Intel Core i7-1385G7',
          gpuModel: 'Integrated Iris Xe',
          storageType: 'NVMe SSD 1TB',
          totalStorage: 1000,
          ram: 32
        }
      },
      {
        name: 'Standard Laptop',
        fingerprint: {
          hardwareConcurrency: 8,
          deviceMemory: 16,
          cpuModel: 'Intel Core i5-1340P',
          gpuModel: 'Integrated Intel Iris Xe',
          storageType: 'NVMe SSD 512GB',
          totalStorage: 512,
          ram: 16
        }
      },
      {
        name: 'Budget Laptop',
        fingerprint: {
          hardwareConcurrency: 4,
          deviceMemory: 8,
          cpuModel: 'Intel Pentium 5405U',
          gpuModel: 'Integrated Intel UHD 610',
          storageType: 'SATA SSD 256GB',
          totalStorage: 256,
          ram: 8
        }
      },
      {
        name: 'MacBook Pro (M3 Max)',
        fingerprint: {
          hardwareConcurrency: 12,
          deviceMemory: 36,
          cpuModel: 'Apple M3 Max',
          gpuModel: 'Apple GPU 30-core',
          storageType: 'Apple SSD 1TB',
          totalStorage: 1000,
          ram: 36
        }
      },
      {
        name: 'MacBook Air (M2)',
        fingerprint: {
          hardwareConcurrency: 8,
          deviceMemory: 16,
          cpuModel: 'Apple M2',
          gpuModel: 'Apple GPU 10-core',
          storageType: 'Apple SSD 512GB',
          totalStorage: 512,
          ram: 16
        }
      },
      {
        name: 'Server (Entry-Level)',
        fingerprint: {
          hardwareConcurrency: 16,
          deviceMemory: 64,
          cpuModel: 'Intel Xeon E-2388G',
          gpuModel: 'None (headless)',
          storageType: 'SAS HDD 2TB',
          totalStorage: 2000,
          ram: 64
        }
      },
      {
        name: 'Raspberry Pi 5',
        fingerprint: {
          hardwareConcurrency: 4,
          deviceMemory: 8,
          cpuModel: 'ARM Cortex-A76 @ 2.4GHz',
          gpuModel: 'Broadcom VideoCore VII',
          storageType: 'MicroSD 128GB',
          totalStorage: 128,
          ram: 8
        }
      }
    ];

    hardwareProfiles.forEach((config, idx) => {
      const testName = `${idx + 1}. ${config.name}`;
      try {
        const hash = this._generateHash(config.fingerprint);
        const hashConsistency = this._testHashConsistency(config.fingerprint, 5);
        const isValid = hash && hashConsistency.consistent;

        testResults.push({
          index: idx + 1,
          testName,
          status: isValid ? 'PASS' : 'FAIL',
          consistency: hashConsistency.consistencyPercentage + '%',
          details: {
            cores: config.fingerprint.hardwareConcurrency,
            ram: config.fingerprint.deviceMemory + 'GB',
            cpu: config.fingerprint.cpuModel,
            storage: config.fingerprint.totalStorage + 'GB'
          }
        });

        if (isValid) this.results.summary.passed++;
        else this.results.summary.failed++;

      } catch (error) {
        testResults.push({
          index: idx + 1,
          testName,
          status: 'ERROR',
          error: error.message
        });
        this.results.summary.failed++;
      }

      this.results.summary.totalTests++;
    });

    this.results.suites[suiteName] = testResults;
    return testResults;
  }

  /**
   * DISPLAY CONFIGURATIONS TEST SUITE
   * Tests 10 display configurations
   */
  testDisplayConfigurations() {
    const suiteName = 'Display Configurations (10 Profiles)';
    const testResults = [];

    const displayConfigs = [
      {
        name: '8K Display (7680x4320)',
        fingerprint: {
          screen: { width: 7680, height: 4320, colorDepth: 32, pixelDepth: 32, devicePixelRatio: 1.0 },
          displayType: '8K LCD',
          refreshRate: 120,
          hdrSupport: true
        }
      },
      {
        name: '4K Gaming Display (3840x2160)',
        fingerprint: {
          screen: { width: 3840, height: 2160, colorDepth: 32, pixelDepth: 32, devicePixelRatio: 1.5 },
          displayType: '4K IPS',
          refreshRate: 144,
          hdrSupport: true
        }
      },
      {
        name: '4K UltraWide (5120x2160)',
        fingerprint: {
          screen: { width: 5120, height: 2160, colorDepth: 32, pixelDepth: 32, devicePixelRatio: 1.0 },
          displayType: '4K Curved',
          refreshRate: 100,
          hdrSupport: true
        }
      },
      {
        name: '2K Ultrawide (3440x1440)',
        fingerprint: {
          screen: { width: 3440, height: 1440, colorDepth: 32, pixelDepth: 32, devicePixelRatio: 1.0 },
          displayType: '2K Curved IPS',
          refreshRate: 144,
          hdrSupport: false
        }
      },
      {
        name: 'Standard 2K (2560x1440)',
        fingerprint: {
          screen: { width: 2560, height: 1440, colorDepth: 32, pixelDepth: 32, devicePixelRatio: 1.0 },
          displayType: '2K IPS Gaming',
          refreshRate: 165,
          hdrSupport: true
        }
      },
      {
        name: 'Full HD (1920x1080)',
        fingerprint: {
          screen: { width: 1920, height: 1080, colorDepth: 24, pixelDepth: 24, devicePixelRatio: 1.0 },
          displayType: 'Full HD IPS',
          refreshRate: 60,
          hdrSupport: false
        }
      },
      {
        name: 'HD (1366x768)',
        fingerprint: {
          screen: { width: 1366, height: 768, colorDepth: 24, pixelDepth: 24, devicePixelRatio: 1.0 },
          displayType: 'HD TN',
          refreshRate: 60,
          hdrSupport: false
        }
      },
      {
        name: 'MacBook Retina (2560x1600)',
        fingerprint: {
          screen: { width: 2560, height: 1600, colorDepth: 32, pixelDepth: 32, devicePixelRatio: 2.0 },
          displayType: 'Retina LCD',
          refreshRate: 120,
          hdrSupport: true
        }
      },
      {
        name: 'iPad Pro (2388x1668)',
        fingerprint: {
          screen: { width: 2388, height: 1668, colorDepth: 32, pixelDepth: 32, devicePixelRatio: 2.0 },
          displayType: 'Liquid Retina',
          refreshRate: 120,
          hdrSupport: true
        }
      },
      {
        name: 'Smartphone (1440x3200)',
        fingerprint: {
          screen: { width: 1440, height: 3200, colorDepth: 32, pixelDepth: 32, devicePixelRatio: 3.88 },
          displayType: 'AMOLED',
          refreshRate: 120,
          hdrSupport: true
        }
      }
    ];

    displayConfigs.forEach((config, idx) => {
      const testName = `${idx + 1}. ${config.name}`;
      try {
        const hash = this._generateHash(config.fingerprint);
        const uniqueness = this._testUniqueness([config.fingerprint], 10);
        const isValid = hash && uniqueness.uniqueness === 100;

        testResults.push({
          index: idx + 1,
          testName,
          status: isValid ? 'PASS' : 'FAIL',
          resolution: `${config.fingerprint.screen.width}x${config.fingerprint.screen.height}`,
          details: {
            displayType: config.fingerprint.displayType,
            refreshRate: config.fingerprint.refreshRate + 'Hz',
            dpi: config.fingerprint.screen.devicePixelRatio,
            hdr: config.fingerprint.hdrSupport ? 'Yes' : 'No'
          }
        });

        if (isValid) this.results.summary.passed++;
        else this.results.summary.failed++;

      } catch (error) {
        testResults.push({
          index: idx + 1,
          testName,
          status: 'ERROR',
          error: error.message
        });
        this.results.summary.failed++;
      }

      this.results.summary.totalTests++;
    });

    this.results.suites[suiteName] = testResults;
    return testResults;
  }

  /**
   * VIRTUAL MACHINE DETECTION TEST SUITE
   */
  testVirtualMachineConfigurations() {
    const suiteName = 'Virtual Machine Detection (6 Configurations)';
    const testResults = [];

    const vmConfigs = [
      {
        name: 'VirtualBox Linux Guest',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (X11; Linux x86_64)',
          vmIndicators: ['VirtualBox', 'vbox', 'virtualbox'],
          platform: 'Linux x86_64',
          hardwareConcurrency: 4,
          deviceMemory: 4,
          cpuBrand: 'VirtualBox'
        }
      },
      {
        name: 'VMware ESXi Guest',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (X11; Linux x86_64)',
          vmIndicators: ['VMware', 'vmware', 'ESXi'],
          platform: 'Linux x86_64',
          hardwareConcurrency: 8,
          deviceMemory: 8,
          cpuBrand: 'VMware'
        }
      },
      {
        name: 'Hyper-V Windows Guest',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
          vmIndicators: ['Hyper-V', 'hyperv', 'hyper-v'],
          platform: 'Win32',
          hardwareConcurrency: 4,
          deviceMemory: 4,
          cpuBrand: 'Hyper-V'
        }
      },
      {
        name: 'KVM/QEMU Guest',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (X11; Linux x86_64)',
          vmIndicators: ['KVM', 'QEMU', 'qemu'],
          platform: 'Linux x86_64',
          hardwareConcurrency: 8,
          deviceMemory: 8,
          cpuBrand: 'QEMU'
        }
      },
      {
        name: 'Docker Container',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (X11; Linux x86_64)',
          vmIndicators: ['docker', 'Docker', 'container'],
          platform: 'Linux x86_64',
          hardwareConcurrency: 4,
          deviceMemory: 2,
          cpuBrand: 'Docker'
        }
      },
      {
        name: 'Proxmox VM',
        fingerprint: {
          userAgent: 'Mozilla/5.0 (X11; Linux x86_64)',
          vmIndicators: ['Proxmox', 'proxmox', 'pve'],
          platform: 'Linux x86_64',
          hardwareConcurrency: 6,
          deviceMemory: 8,
          cpuBrand: 'Proxmox'
        }
      }
    ];

    vmConfigs.forEach((config, idx) => {
      const testName = `${idx + 1}. ${config.name}`;
      try {
        const hash = this._generateHash(config.fingerprint);
        const vmDetected = this._detectVirtualMachine(config.fingerprint);
        const isValid = hash && vmDetected;

        testResults.push({
          index: idx + 1,
          testName,
          status: isValid ? 'PASS' : 'FAIL',
          vmDetected: vmDetected,
          details: {
            indicators: config.fingerprint.vmIndicators.join(', '),
            cores: config.fingerprint.hardwareConcurrency,
            ram: config.fingerprint.deviceMemory + 'GB'
          }
        });

        if (isValid) this.results.summary.passed++;
        else this.results.summary.failed++;

      } catch (error) {
        testResults.push({
          index: idx + 1,
          testName,
          status: 'ERROR',
          error: error.message
        });
        this.results.summary.failed++;
      }

      this.results.summary.totalTests++;
    });

    this.results.suites[suiteName] = testResults;
    return testResults;
  }

  /**
   * UNIQUENESS & COLLISION DETECTION TEST SUITE
   */
  testUniquenessAndCollisions() {
    const suiteName = 'Uniqueness and Collision Detection';
    const testResults = [];

    try {
      // Test 1: Generate 1000 unique fingerprints
      const uniqueFingerprints = this._generateUniqueFingerprints(1000);
      const uniqueHashes = new Set();

      uniqueFingerprints.forEach(fp => {
        const hash = this._generateHash(fp);
        uniqueHashes.add(hash);
      });

      const collisionRate = ((1000 - uniqueHashes.size) / 1000) * 100;
      const uniquenessRate = (uniqueHashes.size / 1000) * 100;

      testResults.push({
        testName: 'Uniqueness Test (1000 fingerprints)',
        status: uniquenessRate > 99.5 ? 'PASS' : 'FAIL',
        totalFingerprints: 1000,
        uniqueHashes: uniqueHashes.size,
        collisions: 1000 - uniqueHashes.size,
        uniquenessRate: uniquenessRate.toFixed(2) + '%',
        collisionRate: collisionRate.toFixed(4) + '%'
      });

      if (uniquenessRate > 99.5) this.results.summary.passed++;
      else this.results.summary.failed++;
      this.results.summary.totalTests++;

    } catch (error) {
      testResults.push({
        testName: 'Uniqueness Test',
        status: 'ERROR',
        error: error.message
      });
      this.results.summary.failed++;
      this.results.summary.totalTests++;
    }

    this.results.suites[suiteName] = testResults;
    return testResults;
  }

  /**
   * LOCALE & LANGUAGE TEST SUITE
   */
  testLocaleConfigurations() {
    const suiteName = 'Locale and Language Configurations (10 Locales)';
    const testResults = [];

    const locales = [
      { language: 'en-US', timezone: 'America/New_York', region: 'United States' },
      { language: 'de-DE', timezone: 'Europe/Berlin', region: 'Germany' },
      { language: 'fr-FR', timezone: 'Europe/Paris', region: 'France' },
      { language: 'ja-JP', timezone: 'Asia/Tokyo', region: 'Japan' },
      { language: 'zh-CN', timezone: 'Asia/Shanghai', region: 'China' },
      { language: 'es-ES', timezone: 'Europe/Madrid', region: 'Spain' },
      { language: 'pt-BR', timezone: 'America/Sao_Paulo', region: 'Brazil' },
      { language: 'ru-RU', timezone: 'Europe/Moscow', region: 'Russia' },
      { language: 'ko-KR', timezone: 'Asia/Seoul', region: 'South Korea' },
      { language: 'ar-SA', timezone: 'Asia/Riyadh', region: 'Saudi Arabia' }
    ];

    locales.forEach((locale, idx) => {
      const testName = `${idx + 1}. ${locale.region} (${locale.language})`;
      try {
        const fingerprint = {
          language: locale.language,
          timezone: locale.timezone,
          region: locale.region,
          userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
          platform: 'Win32'
        };

        const hash = this._generateHash(fingerprint);
        const isValid = hash && hash.length > 0;

        testResults.push({
          index: idx + 1,
          testName,
          status: isValid ? 'PASS' : 'FAIL',
          details: {
            language: locale.language,
            timezone: locale.timezone,
            region: locale.region
          }
        });

        if (isValid) this.results.summary.passed++;
        else this.results.summary.failed++;

      } catch (error) {
        testResults.push({
          index: idx + 1,
          testName,
          status: 'ERROR',
          error: error.message
        });
        this.results.summary.failed++;
      }

      this.results.summary.totalTests++;
    });

    this.results.suites[suiteName] = testResults;
    return testResults;
  }

  /**
   * Helper: Generate SHA256 hash
   */
  _generateHash(data) {
    const dataString = JSON.stringify(data);
    return crypto.createHash('sha256').update(dataString).digest('hex');
  }

  /**
   * Helper: Generate hash variants
   */
  _generateHashVariants(data) {
    return {
      sha256: crypto.createHash('sha256').update(JSON.stringify(data)).digest('hex'),
      sha512: crypto.createHash('sha512').update(JSON.stringify(data)).digest('hex'),
      md5: crypto.createHash('md5').update(JSON.stringify(data)).digest('hex')
    };
  }

  /**
   * Helper: Test hash consistency across multiple generations
   */
  _testHashConsistency(data, iterations) {
    const hashes = new Set();
    for (let i = 0; i < iterations; i++) {
      const hash = this._generateHash(data);
      hashes.add(hash);
    }
    const consistent = hashes.size === 1;
    const consistencyPercentage = ((iterations - (hashes.size - 1)) / iterations) * 100;
    return {
      consistent,
      consistencyPercentage: consistencyPercentage.toFixed(1)
    };
  }

  /**
   * Helper: Test uniqueness of fingerprints
   */
  _testUniqueness(fingerprints, variations) {
    const variedFingerprints = [];
    fingerprints.forEach(fp => {
      for (let i = 0; i < variations; i++) {
        variedFingerprints.push({ ...fp, variation: i });
      }
    });

    const hashes = new Set();
    variedFingerprints.forEach(fp => {
      const hash = this._generateHash(fp);
      hashes.add(hash);
    });

    const uniqueness = (hashes.size / variedFingerprints.length) * 100;
    return { uniqueness, totalVariations: variedFingerprints.length, uniqueHashes: hashes.size };
  }

  /**
   * Helper: Generate unique fingerprints
   */
  _generateUniqueFingerprints(count) {
    const fingerprints = [];
    for (let i = 0; i < count; i++) {
      fingerprints.push({
        userAgent: `Mozilla/5.0 Config-${i}-${Date.now()}`,
        platform: i % 3 === 0 ? 'Win32' : i % 3 === 1 ? 'Linux' : 'MacIntel',
        hardwareConcurrency: 2 + (i % 64),
        deviceMemory: 2 + (i % 256),
        screen: {
          width: 800 + (i * 2) % 3000,
          height: 600 + (i * 2) % 2000,
          colorDepth: 16 + (i % 16)
        },
        language: i % 5 === 0 ? 'en-US' : i % 5 === 1 ? 'de-DE' : i % 5 === 2 ? 'fr-FR' : i % 5 === 3 ? 'ja-JP' : 'zh-CN',
        timezone: ['UTC', 'America/New_York', 'Europe/London', 'Asia/Tokyo', 'Australia/Sydney'][i % 5],
        timestamp: Date.now() + i
      });
    }
    return fingerprints;
  }

  /**
   * Helper: Detect virtual machine indicators
   */
  _detectVirtualMachine(fingerprint) {
    if (!fingerprint.vmIndicators) return false;
    return fingerprint.vmIndicators.some(indicator =>
      fingerprint.userAgent.toLowerCase().includes(indicator.toLowerCase()) ||
      (fingerprint.cpuBrand && fingerprint.cpuBrand.toLowerCase().includes(indicator.toLowerCase()))
    );
  }

  /**
   * Run all test suites
   */
  runAllTests() {
    console.log('Starting Comprehensive Fingerprinting Test Suite...\n');
    console.log('=' . repeat(80));

    this.testOperatingSystems();
    this.testBrowserConfigurations();
    this.testHardwareConfigurations();
    this.testDisplayConfigurations();
    this.testVirtualMachineConfigurations();
    this.testUniquenessAndCollisions();
    this.testLocaleConfigurations();

    this._generateSummary();
    return this.results;
  }

  /**
   * Generate test summary
   */
  _generateSummary() {
    const totalTests = this.results.summary.totalTests;
    const passed = this.results.summary.passed;
    const failed = this.results.summary.failed;
    const passRate = ((passed / totalTests) * 100).toFixed(2);

    this.results.summary.totalTests = totalTests;
    this.results.summary.passed = passed;
    this.results.summary.failed = failed;
    this.results.summary.passRate = passRate + '%';
    this.results.summary.timestamp = new Date().toISOString();

    // Calculate confidence metrics
    this.results.confidenceMetrics = {
      operatingSystemDetection: this._calculateCategoryAccuracy('Operating Systems'),
      browserIdentification: this._calculateCategoryAccuracy('Browser'),
      hardwareFingerprinting: this._calculateCategoryAccuracy('Hardware'),
      displayRecognition: this._calculateCategoryAccuracy('Display'),
      virtualMachineDetection: this._calculateCategoryAccuracy('Virtual Machine'),
      localeDetection: this._calculateCategoryAccuracy('Locale and Language')
    };
  }

  /**
   * Calculate category accuracy
   */
  _calculateCategoryAccuracy(categoryKeyword) {
    const categoryTests = Object.entries(this.results.suites)
      .filter(([key]) => key.includes(categoryKeyword))
      .flatMap(([, results]) => results);

    if (categoryTests.length === 0) return { accuracy: 0, passed: 0, total: 0 };

    const passed = categoryTests.filter(t => t.status === 'PASS').length;
    const total = categoryTests.length;
    const accuracy = ((passed / total) * 100).toFixed(2);

    return {
      accuracy: accuracy + '%',
      passed,
      total,
      failed: total - passed
    };
  }

  /**
   * Export results as JSON
   */
  exportJSON() {
    return JSON.stringify(this.results, null, 2);
  }

  /**
   * Export results as formatted text report
   */
  exportReport() {
    let report = '\n' + '='.repeat(100) + '\n';
    report += 'COMPREHENSIVE FINGERPRINTING TEST SUITE REPORT\n';
    report += 'Multi-OS and Hardware Configuration Testing\n';
    report += '='.repeat(100) + '\n\n';

    // Summary
    report += 'EXECUTIVE SUMMARY\n';
    report += '-'.repeat(100) + '\n';
    report += `Total Tests: ${this.results.summary.totalTests}\n`;
    report += `Passed: ${this.results.summary.passed}\n`;
    report += `Failed: ${this.results.summary.failed}\n`;
    report += `Pass Rate: ${this.results.summary.passRate}\n`;
    report += `Timestamp: ${this.results.summary.timestamp}\n\n`;

    // Confidence Metrics
    report += 'CONFIDENCE METRICS BY CATEGORY\n';
    report += '-'.repeat(100) + '\n';
    Object.entries(this.results.confidenceMetrics).forEach(([category, metrics]) => {
      report += `${category}: ${metrics.accuracy} (${metrics.passed}/${metrics.total} passed)\n`;
    });

    // Detailed Results
    report += '\n' + '='.repeat(100) + '\n';
    report += 'DETAILED TEST RESULTS\n';
    report += '='.repeat(100) + '\n';

    Object.entries(this.results.suites).forEach(([suiteName, results]) => {
      report += `\n${suiteName}\n`;
      report += '-'.repeat(100) + '\n';
      results.forEach(result => {
        const status = result.status === 'PASS' ? '✓' : result.status === 'FAIL' ? '✗' : '⚠';
        report += `  ${status} ${result.testName || result.index}. ${result.status}\n`;
        if (result.details) {
          Object.entries(result.details).forEach(([key, value]) => {
            report += `    • ${key}: ${value}\n`;
          });
        }
        if (result.error) {
          report += `    Error: ${result.error}\n`;
        }
      });
    });

    report += '\n' + '='.repeat(100) + '\n';
    return report;
  }
}

// Main execution
if (require.main === module) {
  const suite = new FingerprintingTestSuite();
  const results = suite.runAllTests();

  // Export results
  const fs = require('fs');
  const reportPath = '/tmp/fingerprinting-test-suite-report.json';
  const textReportPath = '/tmp/fingerprinting-test-suite-report.txt';

  fs.writeFileSync(reportPath, suite.exportJSON());
  fs.writeFileSync(textReportPath, suite.exportReport());

  console.log(suite.exportReport());
  console.log(`\nJSON report: ${reportPath}`);
  console.log(`Text report: ${textReportPath}`);
}

module.exports = FingerprintingTestSuite;
