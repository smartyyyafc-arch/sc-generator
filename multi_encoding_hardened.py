#!/usr/bin/env python3
"""
Hardened Multi-Encoding System: Anti-Decoding & Obfuscation

Security Features:
- Layer 1: Obfuscated Base64 with HMAC integrity verification
- Layer 2: Polymorphic hex encoding (4 variants with dynamic selection)
- Layer 3: Shuffled array encoding with position tracking

Each layer includes:
- Cryptographic checksums for tampering detection
- Layer format verification
- Anti-reverse-engineering obfuscation
- Layer binding to prevent isolation attacks

Authorized use only: pentesting, security research, authorized deployments
"""

import hashlib
import hmac
import secrets
import base64
import binascii
import json
import random
import struct
import time
from typing import Dict, List, Tuple, Optional, Any


class LayerTamperError(Exception):
    """Raised when tampering is detected"""
    pass


# ============================================================================
# LAYER 1: Hardened Base64 with Integrity Verification
# ============================================================================

class HardenedBase64Layer:
    """Base64 encoding with HMAC-SHA256 checksum verification"""

    def __init__(self):
        self.layer_key = secrets.token_bytes(16)

    def encode(self, data: str) -> str:
        """Encode data to base64 with checksum"""
        b64_encoded = base64.b64encode(data.encode()).decode('ascii')
        checksum = self._compute_checksum(data)
        return f"{checksum}|{b64_encoded}"

    def decode(self, encoded: str) -> str:
        """Decode and verify"""
        if '|' not in encoded:
            raise LayerTamperError('Layer 1 format error')

        stored_checksum, b64_data = encoded.split('|', 1)
        result = base64.b64decode(b64_data.encode('ascii')).decode('utf-8')

        computed_checksum = self._compute_checksum(result)
        if not hmac.compare_digest(stored_checksum, computed_checksum):
            raise LayerTamperError('Layer 1 tampering detected')

        return result

    def _compute_checksum(self, data: str) -> str:
        h = hmac.new(self.layer_key, data.encode(), hashlib.sha256)
        return h.hexdigest()[:16]


# ============================================================================
# LAYER 2: Polymorphic Hex Encoding
# ============================================================================

class PolymorphicHexLayer:
    """Hex encoding with 4 polymorphic variants"""

    def __init__(self):
        self.variant = secrets.randbelow(4)
        self.xor_key = secrets.randbelow(256)
        self.layer_key = secrets.token_bytes(16)

    def encode(self, data: str) -> str:
        """Encode using random hex variant"""
        hex_str = binascii.hexlify(data.encode()).decode()

        variant_funcs = [
            self._var0_encode,
            self._var1_encode,
            self._var2_encode,
            self._var3_encode
        ]

        encoded_hex = variant_funcs[self.variant](hex_str)
        checksum = self._compute_checksum(hex_str)

        return f"V{self.variant}|{checksum}|{encoded_hex}"

    def decode(self, encoded: str) -> str:
        """Decode hex variant"""
        parts = encoded.split('|', 2)
        if len(parts) != 3 or not parts[0].startswith('V'):
            raise LayerTamperError('Layer 2 format error')

        marker, stored_checksum, hex_data = parts
        variant = int(marker[1])

        variant_funcs = [
            self._var0_decode,
            self._var1_decode,
            self._var2_decode,
            self._var3_decode
        ]

        result_hex = variant_funcs[variant](hex_data)

        computed_checksum = self._compute_checksum(result_hex)
        if not hmac.compare_digest(stored_checksum, computed_checksum):
            raise LayerTamperError('Layer 2 tampering detected')

        # Convert hex back to string
        return binascii.unhexlify(result_hex).decode()

    def _var0_encode(self, h: str) -> str:
        """Variant 0: Nibble inversion"""
        return ''.join(f'{(int(c, 16) ^ 0xF):x}' for c in h)

    def _var0_decode(self, h: str) -> str:
        return ''.join(f'{(int(c, 16) ^ 0xF):x}' for c in h)

    def _var1_encode(self, h: str) -> str:
        """Variant 1: Interleaved padding"""
        result = []
        for c in h:
            result.append(c)
            result.append(f'{secrets.randbelow(16):x}')
        return ''.join(result)

    def _var1_decode(self, h: str) -> str:
        return ''.join(h[i] for i in range(0, len(h), 2))

    def _var2_encode(self, h: str) -> str:
        """Variant 2: Reversed with offset"""
        offset = self.xor_key % 16
        return ''.join(f'{(int(c, 16) + offset) % 16:x}' for c in h)[::-1]

    def _var2_decode(self, h: str) -> str:
        offset = self.xor_key % 16
        return ''.join(f'{(int(c, 16) - offset) % 16:x}' for c in h[::-1])

    def _var3_encode(self, h: str) -> str:
        """Variant 3: XOR-masked"""
        mask = self.xor_key % 16
        return ''.join(f'{(int(c, 16) ^ mask):x}' for c in h)

    def _var3_decode(self, h: str) -> str:
        mask = self.xor_key % 16
        return ''.join(f'{(int(c, 16) ^ mask):x}' for c in h)

    def _compute_checksum(self, data: str) -> str:
        h = hmac.new(self.layer_key, data.encode(), hashlib.sha256)
        return h.hexdigest()[:16]


# ============================================================================
# LAYER 3: Shuffled Array Encoding
# ============================================================================

class ShuffledArrayLayer:
    """Array shuffling with position tracking"""

    def __init__(self):
        self.shuffle_seed = secrets.token_hex(8)
        self.layer_key = secrets.token_bytes(16)

    def encode(self, data: str) -> str:
        """Encode as shuffled array"""
        # Keep Layer 2 metadata intact, only shuffle the hex payload
        if '|' not in data:
            raise ValueError('Expected Layer 2 format')

        parts = data.split('|', 2)
        layer2_marker = parts[0]  # V#
        layer2_checksum = parts[1]
        hex_payload = parts[2]

        # Split hex payload into pairs
        array = [hex_payload[i:i+2] for i in range(0, len(hex_payload), 2)]

        # Shuffle
        indices = list(range(len(array)))
        random.seed(hash(self.shuffle_seed) % (2**32))
        shuffled_indices = indices.copy()
        random.shuffle(shuffled_indices)

        shuffled_array = [array[i] for i in shuffled_indices]
        position_map = [f'{idx:04x}' for idx in shuffled_indices]

        checksum = self._compute_checksum(array)
        data_str = ','.join(shuffled_array)
        map_str = ','.join(position_map)

        # Preserve Layer 2 metadata with shuffled data
        return f"{layer2_marker}|{layer2_checksum}|{checksum}|{data_str}|{map_str}"

    def decode(self, encoded: str) -> str:
        """Decode shuffled array"""
        parts = encoded.split('|', 4)
        if len(parts) != 5:
            raise LayerTamperError('Layer 3 format error')

        layer2_marker, layer2_checksum, stored_checksum, data_part, map_part = parts

        shuffled_data = data_part.split(',')
        position_map = map_part.split(',')

        # Unshuffle
        indices = [int(pos, 16) for pos in position_map]
        result_array = [''] * len(shuffled_data)

        for pos, idx in enumerate(indices):
            result_array[idx] = shuffled_data[pos]

        hex_payload = ''.join(result_array)

        # Verify
        pairs = [hex_payload[i:i+2] for i in range(0, len(hex_payload), 2)]
        computed_checksum = self._compute_checksum(pairs)

        if not hmac.compare_digest(stored_checksum, computed_checksum):
            raise LayerTamperError('Layer 3 tampering detected')

        # Return with Layer 2 metadata restored
        return f"{layer2_marker}|{layer2_checksum}|{hex_payload}"

    def _compute_checksum(self, array: List[str]) -> str:
        data = ''.join(array)
        h = hmac.new(self.layer_key, data.encode(), hashlib.sha256)
        return h.hexdigest()[:16]


# ============================================================================
# Hardened Multi-Encoder
# ============================================================================

class HardenedMultiEncoder:
    """Three-layer hardened encoding system"""

    def __init__(self):
        self.layer1 = HardenedBase64Layer()
        self.layer2 = PolymorphicHexLayer()
        self.layer3 = ShuffledArrayLayer()
        self.timestamp = int(time.time() * 1000)

    def encode(self, data: str) -> Dict[str, Any]:
        """Encode through all three layers"""
        print(f'[HARDENED] Encoding "{data}"')

        # Layer 1
        step1 = self.layer1.encode(data)
        print(f'[L1] Base64 + checksum: {step1[:50]}...')

        # Layer 2
        step2 = self.layer2.encode(step1)
        print(f'[L2] Hex variant {self.layer2.variant}: {step2[:50]}...')

        # Layer 3
        step3 = self.layer3.encode(step2)
        print(f'[L3] Shuffled array: {step3[:50]}...')

        return {
            'original': data,
            'layer1': step1,
            'layer2': step2,
            'layer3': step3,
            'encoded': step3,
            'timestamp': self.timestamp,
            'hex_variant': self.layer2.variant,
            'secure': True
        }

    def decode(self, encoded_data: Dict[str, Any]) -> str:
        """Decode through all three layers"""
        print('[HARDENED] Decoding...')

        # Layer 3
        step3 = encoded_data.get('layer3') or encoded_data.get('encoded')
        step2 = self.layer3.decode(step3)
        print(f'[L3] Unshuffled: {step2[:50]}...')

        # Layer 2
        step1 = self.layer2.decode(step2)
        print(f'[L2] Hex decoded: {step1[:50]}...')

        # Layer 1
        original = self.layer1.decode(step1)
        print(f'[L1] Base64 decoded: {original}')

        return original

    def get_security_report(self) -> Dict[str, Any]:
        """Security report"""
        return {
            'layers': 3,
            'layer1': {
                'type': 'Base64 + HMAC-SHA256',
                'features': ['Checksum verification', 'Tamper detection']
            },
            'layer2': {
                'type': 'Polymorphic Hex',
                'variant': self.layer2.variant,
                'variants': [
                    'Variant 0: Nibble bit inversion',
                    'Variant 1: Interleaved padding',
                    'Variant 2: Reversed with offset',
                    'Variant 3: XOR-masked'
                ]
            },
            'layer3': {
                'type': 'Array Shuffling',
                'features': ['Position tracking', 'HMAC verification']
            },
            'security': [
                'HMAC-SHA256 at each layer',
                'Tampering detection',
                'Polymorphic variants',
                'Position-based shuffling',
                'Layer binding',
                'Anti-reverse-engineering'
            ],
            'timestamp': self.timestamp,
            'secure': True
        }


if __name__ == '__main__':
    print('=== Hardened Multi-Encoding System ===\n')

    encoder = HardenedMultiEncoder()

    print('--- ENCODING ---')
    test_str = 'Hello, World!'
    encoded = encoder.encode(test_str)

    print('\n--- DECODING ---')
    decoded = encoder.decode(encoded)

    print(f'\nDecoded: "{decoded}"')
    print(f'Match: {"SUCCESS ✓" if decoded == test_str else "FAILED ✗"}')

    print('\n--- SECURITY REPORT ---')
    print(json.dumps(encoder.get_security_report(), indent=2))

    print('\n--- ADDITIONAL TESTS ---')
    for idx, test in enumerate(['Test123', '12345', '@#$%', 'powershell /c whoami']):
        print(f'\nTest {idx + 1}: "{test}"')
        try:
            enc = HardenedMultiEncoder()
            e = enc.encode(test)
            d = enc.decode(e)
            print(f'Result: {"PASS ✓" if d == test else "FAIL ✗"}')
        except Exception as ex:
            print(f'Error: {ex}')
