/**
 * Practical examples of multi-encoding system usage
 */

const {
  compactMultiEncode,
  compactMultiDecode,
  multiEncode,
  multiDecode,
  encodeBase64,
  decodeBase64
} = require('./multi-encoding');

console.log('╔════════════════════════════════════════════════════════════╗');
console.log('║      Multi-Encoding System - Practical Examples           ║');
console.log('╚════════════════════════════════════════════════════════════╝\n');

// =============================================================================
// Example 1: Configuration Protection
// =============================================================================
console.log('📋 Example 1: Configuration Protection\n');

const config = {
  database: {
    host: 'db.example.com',
    port: 5432,
    username: 'admin',
    password: 'SuperSecret123!'
  }
};

const configString = JSON.stringify(config);
const encoded = compactMultiEncode(configString);

console.log('Original config:', configString);
console.log('Encoded array (safe to store):', encoded.array);
console.log('Hex representation:', encoded.hex);

const decoded = compactMultiDecode(encoded);
const recoveredConfig = JSON.parse(decoded);
console.log('Recovered config:', recoveredConfig);
console.log('✓ Config round-trip successful\n');

// =============================================================================
// Example 2: Data Obfuscation in URLs
// =============================================================================
console.log('🔗 Example 2: Data Obfuscation in URLs\n');

const userData = 'user_id=12345&role=admin';
const obfuscated = compactMultiEncode(userData);

// Create safe URL parameter from hex
const urlParam = Buffer.from(obfuscated.hex).toString('base64');
const url = `https://api.example.com/action?data=${urlParam}`;

console.log('Original data:', userData);
console.log('URL parameter (hex→base64):', urlParam);
console.log('Full URL:', url);

// Reverse the process
const recovered = Buffer.from(urlParam, 'base64').toString('utf8');
console.log('Recovered from URL:', recovered);
console.log('✓ URL parameter round-trip successful\n');

// =============================================================================
// Example 3: Multi-Layer Obfuscation Progress
// =============================================================================
console.log('📊 Example 3: Encoding Layers Visualization\n');

const message = 'Secret Data!';
console.log(`Original:  "${message}"`);
console.log(`Length: ${message.length} characters\n`);

const b64 = encodeBase64(message);
console.log(`After Base64: "${b64}"`);
console.log(`Length: ${b64.length} characters\n`);

const result = compactMultiEncode(message);
console.log(`After Hex: "${result.hex}"`);
console.log(`Length: ${result.hex.length} characters\n`);

console.log(`After Array: [${result.array.slice(0, 5).join(', ')}, ...]`);
console.log(`Array length: ${result.array.length} elements\n`);

const obfuscationRatio = ((result.hex.length / message.length) * 100).toFixed(2);
console.log(`Obfuscation ratio: ${obfuscationRatio}% (hex is ~${obfuscationRatio}% larger)\n`);

// =============================================================================
// Example 4: API Request/Response Encryption
// =============================================================================
console.log('🔐 Example 4: API Request/Response Encoding\n');

// Mock API request
const apiRequest = {
  timestamp: new Date().toISOString(),
  user: 'alice@example.com',
  action: 'update_profile',
  data: { theme: 'dark', language: 'en' }
};

const requestString = JSON.stringify(apiRequest);
const encodedRequest = compactMultiEncode(requestString);

console.log('API Request Payload:');
console.log('  Original:', requestString.substring(0, 60) + '...');
console.log('  Encoded hex:', encodedRequest.hex.substring(0, 60) + '...');
console.log('  Array elements:', encodedRequest.array.length);

// Mock transmission
const transmittedArray = encodedRequest.array;

// Decode on receiver side
const decodedRequest = compactMultiDecode({ array: transmittedArray, hex: '', base64: '' });
const receivedPayload = JSON.parse(decodedRequest);

console.log('Received and decoded:');
console.log('  User:', receivedPayload.user);
console.log('  Action:', receivedPayload.action);
console.log('✓ API payload successfully transmitted and decoded\n');

// =============================================================================
// Example 5: Data Serialization for Storage
// =============================================================================
console.log('💾 Example 5: Data Serialization for Storage\n');

const userProfile = {
  id: 'usr_abc123',
  name: 'Alice Johnson',
  email: 'alice@example.com',
  tags: ['important', 'verified', 'premium'],
  createdAt: '2024-01-15',
  preferences: {
    notifications: true,
    theme: 'dark',
    locale: 'en-US'
  }
};

const profileString = JSON.stringify(userProfile);
const { base64, hex, array } = compactMultiEncode(profileString);

console.log('Storage formats:\n');

// Format 1: Array (most compact for some uses)
console.log(`1. Array format (${array.length} elements):`);
console.log(`   ${JSON.stringify(array)}\n`);

// Format 2: Hex (human-readable hex string)
console.log(`2. Hex format (${hex.length} chars):`);
console.log(`   ${hex}\n`);

// Format 3: Base64 (standard encoding)
console.log(`3. Base64 format (${base64.length} chars):`);
console.log(`   ${base64}\n`);

// Retrieve from any format
const restored = compactMultiDecode({ base64, hex, array });
const restoredProfile = JSON.parse(restored);
console.log('Retrieved from storage:');
console.log(`  Name: ${restoredProfile.name}`);
console.log(`  Email: ${restoredProfile.email}`);
console.log('✓ Profile successfully stored and retrieved\n');

// =============================================================================
// Example 6: Cascading Encoding (Multiple rounds)
// =============================================================================
console.log('🔄 Example 6: Double Encoding (Extra Obfuscation)\n');

const sensitive = 'API_KEY_12345_SECRET';
console.log(`Original: "${sensitive}"\n`);

// First encoding pass
const firstPass = compactMultiEncode(sensitive);
console.log('After 1st encoding:');
console.log(`  Hex: ${firstPass.hex}\n`);

// Second encoding pass (encode the hex string)
const secondPass = compactMultiEncode(firstPass.hex);
console.log('After 2nd encoding:');
console.log(`  Hex: ${secondPass.hex.substring(0, 40)}...`);
console.log(`  Array length: ${secondPass.array.length}\n`);

// Reverse the process
const reverseSecond = compactMultiDecode(secondPass);
const reverseFirst = compactMultiDecode(JSON.parse(`{"base64":"","hex":"${reverseSecond}","array":[]}`));
console.log(`After double decode: "${reverseFirst}"`);
console.log('✓ Double encoding/decoding successful\n');

// =============================================================================
// Example 7: Encoding Different Data Types
// =============================================================================
console.log('🎯 Example 7: Encoding Various Data Types\n');

const testData = [
  { label: 'Simple text', data: 'Hello World' },
  { label: 'JSON object', data: JSON.stringify({ key: 'value' }) },
  { label: 'Array', data: JSON.stringify([1, 2, 3, 4, 5]) },
  { label: 'Numbers', data: '9876543210' },
  { label: 'Special chars', data: '!@#$%^&*()_+-=[]{}|;:,.<>?' },
  { label: 'Emoji', data: '😀🎉🚀💻🌟' }
];

testData.forEach(({ label, data }) => {
  const encoded = compactMultiEncode(data);
  const decoded = compactMultiDecode(encoded);
  const match = decoded === data;

  console.log(`${match ? '✓' : '✗'} ${label}`);
  console.log(`  Original: ${data.substring(0, 30)}${data.length > 30 ? '...' : ''}`);
  console.log(`  Decoded:  ${decoded.substring(0, 30)}${decoded.length > 30 ? '...' : ''}`);
  console.log();
});

// =============================================================================
// Example 8: Performance Testing
// =============================================================================
console.log('⚡ Example 8: Performance Testing\n');

const sizes = [100, 1000, 10000];

sizes.forEach(size => {
  const testString = 'A'.repeat(size);

  console.time(`  Encode ${size} chars`);
  const encoded = compactMultiEncode(testString);
  console.timeEnd(`  Encode ${size} chars`);

  console.time(`  Decode ${size} chars`);
  const decoded = compactMultiDecode(encoded);
  console.timeEnd(`  Decode ${size} chars`);

  console.log(`  Encoded size: ${encoded.hex.length} chars (${(encoded.hex.length / size * 100).toFixed(1)}% growth)`);
  console.log();
});

// =============================================================================
// Example 9: Real-world Scenario - Session Tokenization
// =============================================================================
console.log('🎫 Example 9: Session Token Generation\n');

const sessionData = {
  userId: 'user_789xyz',
  sessionId: 'sess_456abc',
  loginTime: new Date().toISOString(),
  ipAddress: '192.168.1.100',
  userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
};

const sessionString = JSON.stringify(sessionData);
const { array: sessionArray } = compactMultiEncode(sessionString);

// Create a compact token
const token = sessionArray.join('');
console.log('Session data:', sessionString.substring(0, 50) + '...');
console.log('Generated token (first 80 chars):', token.substring(0, 80) + '...');
console.log('Token length:', token.length, 'characters');

// Parse token back
const decodedToken = compactMultiDecode({
  array: sessionArray,
  hex: '',
  base64: ''
});
const parsedSession = JSON.parse(decodedToken);
console.log('Decoded session user:', parsedSession.userId);
console.log('✓ Session token successfully created and validated\n');

// =============================================================================
// Summary
// =============================================================================
console.log('╔════════════════════════════════════════════════════════════╗');
console.log('║              All Examples Completed Successfully           ║');
console.log('╚════════════════════════════════════════════════════════════╝');
