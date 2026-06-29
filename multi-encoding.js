/**
 * Multi-Encoding System: Base64 → Hex → Array
 *
 * Each encoding layer transforms the output of the previous layer:
 * 1. Original string → Base64 (text encoding)
 * 2. Base64 → Hex (character codes to hexadecimal)
 * 3. Hex → Array (hex string to array of hex values)
 *
 * Decoder reverses all steps in order.
 */

/**
 * Layer 1: Base64 Encoding
 * Converts a string to Base64 representation
 */
function encodeBase64(input) {
  return Buffer.from(input, 'utf8').toString('base64');
}

function decodeBase64(base64) {
  return Buffer.from(base64, 'base64').toString('utf8');
}

/**
 * Layer 2: Hex Encoding
 * Converts Base64 string to hexadecimal representation
 * Each character becomes its ASCII code in hex (2 digits)
 */
function encodeHex(base64String) {
  let hex = '';
  for (let i = 0; i < base64String.length; i++) {
    const charCode = base64String.charCodeAt(i);
    hex += charCode.toString(16).padStart(2, '0');
  }
  return hex;
}

function decodeHex(hexString) {
  let result = '';
  for (let i = 0; i < hexString.length; i += 2) {
    const hex = hexString.substr(i, 2);
    result += String.fromCharCode(parseInt(hex, 16));
  }
  return result;
}

/**
 * Layer 3: Array Encoding
 * Converts hex string to array of individual hex values
 * Each pair of hex digits becomes one array element
 */
function encodeArray(hexString) {
  const array = [];
  for (let i = 0; i < hexString.length; i += 2) {
    array.push(hexString.substr(i, 2));
  }
  return array;
}

function decodeArray(array) {
  return array.join('');
}

/**
 * Multi-Encoder: Chains all three encoding layers
 * Input → Base64 → Hex → Array
 */
function multiEncode(input) {
  const step1 = encodeBase64(input);
  console.log(`Step 1 (Base64): ${step1}`);

  const step2 = encodeHex(step1);
  console.log(`Step 2 (Hex): ${step2}`);

  const step3 = encodeArray(step2);
  console.log(`Step 3 (Array): ${JSON.stringify(step3)}`);

  return {
    original: input,
    base64: step1,
    hex: step2,
    array: step3
  };
}

/**
 * Multi-Decoder: Reverses all three encoding layers in order
 * Array → Hex → Base64 → Output
 */
function multiDecode(encodedArray) {
  // Step 1: Array to Hex
  const hex = decodeArray(encodedArray.array);
  console.log(`Step 1 (Hex): ${hex}`);

  // Step 2: Hex to Base64
  const base64 = decodeHex(hex);
  console.log(`Step 2 (Base64): ${base64}`);

  // Step 3: Base64 to Original
  const original = decodeBase64(base64);
  console.log(`Step 3 (Original): ${original}`);

  return original;
}

/**
 * Compact multi-encoder: Returns all layers without logging
 */
function compactMultiEncode(input) {
  const base64 = encodeBase64(input);
  const hex = encodeHex(base64);
  const array = encodeArray(hex);

  return { base64, hex, array };
}

/**
 * Compact multi-decoder: Reverses encoding without logging
 */
function compactMultiDecode(encodedData) {
  const hex = decodeArray(encodedData.array);
  const base64 = decodeHex(hex);
  const original = decodeBase64(base64);

  return original;
}

// Export for use as module
module.exports = {
  // Individual layer encoders/decoders
  encodeBase64,
  decodeBase64,
  encodeHex,
  decodeHex,
  encodeArray,
  decodeArray,
  // Multi-layer encoders/decoders (with logging)
  multiEncode,
  multiDecode,
  // Compact versions (without logging)
  compactMultiEncode,
  compactMultiDecode
};

// Example usage
if (require.main === module) {
  console.log('=== Multi-Encoding Demonstration ===\n');

  const testString = 'Hello, World!';
  console.log(`Original Input: "${testString}"\n`);

  console.log('--- ENCODING PROCESS ---');
  const encoded = multiEncode(testString);

  console.log('\n--- DECODING PROCESS ---');
  const decoded = multiDecode(encoded);

  console.log(`\nDecoded Output: "${decoded}"`);
  console.log(`Match: ${decoded === testString ? 'SUCCESS ✓' : 'FAILED ✗'}`);

  // Test with different inputs
  console.log('\n\n=== Additional Test Cases ===\n');

  const testCases = [
    'Multi-Encoding Test',
    '12345',
    'Special chars: @#$%',
    'Emoji: 🚀'
  ];

  testCases.forEach((testCase, index) => {
    console.log(`\nTest ${index + 1}: "${testCase}"`);
    try {
      const enc = compactMultiEncode(testCase);
      const dec = compactMultiDecode(enc);
      console.log(`Result: ${dec === testCase ? 'PASS ✓' : 'FAIL ✗'}`);
    } catch (error) {
      console.log(`Error: ${error.message}`);
    }
  });
}
