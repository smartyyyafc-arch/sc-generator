#!/usr/bin/env python3
"""
Fingerprint-Key Integration System
Integrates FingerprintManager with MultiEncodingKeySystem for unified target management
Provides seamless encoding/decoding with system-specific keys
For authorized pentesting and security research
"""

import json
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

from fingerprint_manager import FingerprintManager, FingerprintConfig
from multi_encoding_key_derivation import (
    MultiEncodingKeySystem,
    KeyDerivationMethod,
    EncodingStrategy,
    DerivedKey,
    EncodingStrategySelector
)


class TargetEncodingMode(Enum):
    """Encoding modes for targets"""
    DETERMINISTIC = "deterministic"  # Same output for same input
    RANDOMIZED = "randomized"        # Different output each time
    HYBRID = "hybrid"                # Mix of both


@dataclass
class EncodedPayload:
    """Encoded payload with metadata"""
    target_id: str
    original: str
    encoded: str
    encoding_strategy: str
    fingerprint_id: str
    key_hash: str
    salt_used: str
    metadata: Dict[str, Any]


class FingerprintKeyIntegration:
    """
    Unified system for managing fingerprints and encoding keys
    Provides target-specific encoding/decoding capabilities
    """

    def __init__(
        self,
        fingerprint_config_dir: str = '/tmp/sc-fingerprints',
        encoding_config_dir: str = '/tmp/sc-encoding-keys'
    ):
        """
        Initialize integrated system

        Args:
            fingerprint_config_dir: Directory for fingerprint configurations
            encoding_config_dir: Directory for encoding key configurations
        """
        self.fingerprint_manager = FingerprintManager(fingerprint_config_dir)
        self.key_system = MultiEncodingKeySystem(encoding_config_dir)

        # Mapping between fingerprints and encoding targets
        self.fingerprint_to_target: Dict[str, str] = {}
        self.target_to_fingerprint: Dict[str, str] = {}

        self._load_mappings()

    def _load_mappings(self):
        """Load fingerprint-target mappings"""
        mappings_file = f"{self.key_system.config_dir}/fingerprint_mappings.json"
        try:
            with open(mappings_file, 'r') as f:
                data = json.load(f)
                self.fingerprint_to_target = data.get('fingerprint_to_target', {})
                self.target_to_fingerprint = data.get('target_to_fingerprint', {})
        except FileNotFoundError:
            pass

    def _save_mappings(self):
        """Save fingerprint-target mappings"""
        mappings_file = f"{self.key_system.config_dir}/fingerprint_mappings.json"
        with open(mappings_file, 'w') as f:
            json.dump({
                'fingerprint_to_target': self.fingerprint_to_target,
                'target_to_fingerprint': self.target_to_fingerprint
            }, f, indent=2)

    def register_fingerprint_with_encoding(
        self,
        fingerprint_id: str,
        target_name: str,
        encoding_strategy: Optional[EncodingStrategy] = None,
        key_derivation_method: Optional[KeyDerivationMethod] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, str]:
        """
        Register a fingerprint and create corresponding encoding target

        Args:
            fingerprint_id: Existing fingerprint ID
            target_name: Name for the encoding target
            encoding_strategy: Encoding strategy (auto-select if None)
            key_derivation_method: Key derivation method
            metadata: Additional metadata

        Returns:
            Tuple of (fingerprint_id, target_id)
        """
        if fingerprint_id not in self.fingerprint_manager.fingerprints:
            raise ValueError(f"Fingerprint {fingerprint_id} not found")

        fingerprint = self.fingerprint_manager.fingerprints[fingerprint_id]

        # Create fingerprint data from modifications
        fingerprint_data = self._extract_fingerprint_data(fingerprint)

        # Create encoding target
        profile = self.key_system.create_target_profile(
            name=target_name,
            fingerprint_data=fingerprint_data,
            encoding_strategy=encoding_strategy,
            key_derivation_method=key_derivation_method,
            metadata=metadata or {}
        )

        # Create bidirectional mapping
        self.fingerprint_to_target[fingerprint_id] = profile.target_id
        self.target_to_fingerprint[profile.target_id] = fingerprint_id
        self._save_mappings()

        # Derive initial key
        self.key_system.derive_key_for_target(profile.target_id)

        return fingerprint_id, profile.target_id

    def _extract_fingerprint_data(self, fingerprint: FingerprintConfig) -> Dict[str, str]:
        """
        Extract fingerprint data suitable for key derivation

        Args:
            fingerprint: FingerprintConfig object

        Returns:
            Dictionary of fingerprint components
        """
        data = {
            'fingerprint_id': fingerprint.id,
            'fingerprint_name': fingerprint.name,
            'description': fingerprint.description
        }

        # Extract structured data from modifications
        mods = fingerprint.modifications

        if 'metadata' in mods:
            meta = mods['metadata']
            for key, value in meta.items():
                data[f'meta_{key}'] = str(value)

        if 'pe_sections' in mods:
            sections = mods['pe_sections']
            for key, value in sections.items():
                data[f'pe_{key}'] = str(value)

        return data

    def encode_payload_for_target(
        self,
        target_id: str,
        payload: str,
        mode: TargetEncodingMode = TargetEncodingMode.DETERMINISTIC
    ) -> EncodedPayload:
        """
        Encode payload for specific target using derived key

        Args:
            target_id: Target identifier
            payload: Payload to encode
            mode: Encoding mode

        Returns:
            EncodedPayload object
        """
        if target_id not in self.key_system.target_profiles:
            raise ValueError(f"Target {target_id} not found")

        # Get derived key
        derived_key = self.key_system.derive_key_for_target(target_id)

        # Get encoding parameters
        params = self.key_system.get_encoding_parameters(target_id)

        # Encode based on strategy
        strategy = derived_key.strategy
        encoded = self._apply_encoding(payload, strategy, params, mode)

        # Get fingerprint ID if mapped
        fingerprint_id = self.target_to_fingerprint.get(target_id, 'unmapped')

        return EncodedPayload(
            target_id=target_id,
            original=payload,
            encoded=encoded,
            encoding_strategy=strategy.value,
            fingerprint_id=fingerprint_id,
            key_hash=derived_key.fingerprint_hash[:16],
            salt_used=derived_key.salt_used,
            metadata={
                'profile_name': self.key_system.target_profiles[target_id].name,
                'key_length': len(derived_key.key),
                'mode': mode.value
            }
        )

    def _apply_encoding(
        self,
        data: str,
        strategy: EncodingStrategy,
        params: Dict[str, Any],
        mode: TargetEncodingMode
    ) -> str:
        """
        Apply encoding to data based on strategy

        Args:
            data: Data to encode
            strategy: Encoding strategy
            params: Strategy parameters
            mode: Encoding mode

        Returns:
            Encoded data
        """
        import base64
        import binascii

        if strategy == EncodingStrategy.HEX:
            return binascii.hexlify(data.encode()).decode()

        elif strategy == EncodingStrategy.BASE64:
            return base64.b64encode(data.encode()).decode()

        elif strategy == EncodingStrategy.ROT13:
            rotation = params.get('rotation', 13)
            result = []
            for char in data:
                if char.isalpha():
                    base = ord('a') if char.islower() else ord('A')
                    shifted = (ord(char) - base + rotation) % 26
                    result.append(chr(base + shifted))
                else:
                    result.append(char)
            return ''.join(result)

        elif strategy == EncodingStrategy.XOR:
            key = params.get('key', 42)
            return ''.join(format(ord(c) ^ key, '02x') for c in data)

        elif strategy == EncodingStrategy.OCTAL:
            hex_str = binascii.hexlify(data.encode()).decode()
            return ''.join(oct(int(hex_str[i:i+2], 16))[2:].zfill(3) for i in range(0, len(hex_str), 2))

        elif strategy == EncodingStrategy.ASCII:
            return ','.join(str(ord(char)) for char in data)

        elif strategy == EncodingStrategy.REVERSE:
            return data[::-1]

        elif strategy == EncodingStrategy.CUSTOM_SUBSTITUTION:
            sub_table = params.get('substitution_table', {})
            return ''.join(sub_table.get(char, char) for char in data)

        else:
            return base64.b64encode(data.encode()).decode()

    def decode_payload_for_target(
        self,
        target_id: str,
        encoded_payload: str
    ) -> str:
        """
        Decode payload for specific target

        Args:
            target_id: Target identifier
            encoded_payload: Encoded payload

        Returns:
            Decoded payload
        """
        if target_id not in self.key_system.target_profiles:
            raise ValueError(f"Target {target_id} not found")

        # Get derived key and parameters
        derived_key = self.key_system.derive_key_for_target(target_id)
        params = self.key_system.get_encoding_parameters(target_id)

        # Decode based on strategy
        strategy = derived_key.strategy
        return self._apply_decoding(encoded_payload, strategy, params)

    def _apply_decoding(
        self,
        data: str,
        strategy: EncodingStrategy,
        params: Dict[str, Any]
    ) -> str:
        """
        Apply decoding to data based on strategy

        Args:
            data: Data to decode
            strategy: Encoding strategy
            params: Strategy parameters

        Returns:
            Decoded data
        """
        import base64
        import binascii

        if strategy == EncodingStrategy.HEX:
            return binascii.unhexlify(data).decode()

        elif strategy == EncodingStrategy.BASE64:
            return base64.b64decode(data).decode()

        elif strategy == EncodingStrategy.ROT13:
            rotation = params.get('rotation', 13)
            result = []
            for char in data:
                if char.isalpha():
                    base = ord('a') if char.islower() else ord('A')
                    shifted = (ord(char) - base - rotation) % 26
                    result.append(chr(base + shifted))
                else:
                    result.append(char)
            return ''.join(result)

        elif strategy == EncodingStrategy.XOR:
            key = params.get('key', 42)
            return ''.join(chr(int(data[i:i+2], 16) ^ key) for i in range(0, len(data), 2))

        elif strategy == EncodingStrategy.OCTAL:
            return ''.join(chr(int(data[i:i+3], 8)) for i in range(0, len(data), 3))

        elif strategy == EncodingStrategy.ASCII:
            return ''.join(chr(int(val)) for val in data.split(','))

        elif strategy == EncodingStrategy.REVERSE:
            return data[::-1]

        elif strategy == EncodingStrategy.CUSTOM_SUBSTITUTION:
            sub_table = params.get('substitution_table', {})
            reverse_table = {v: k for k, v in sub_table.items()}
            return ''.join(reverse_table.get(char, char) for char in data)

        else:
            return base64.b64decode(data).decode()

    def get_integrated_profile(self, target_id: str) -> Dict[str, Any]:
        """
        Get comprehensive integrated profile for target

        Args:
            target_id: Target identifier

        Returns:
            Dictionary with complete profile information
        """
        if target_id not in self.key_system.target_profiles:
            raise ValueError(f"Target {target_id} not found")

        # Get base configuration
        config = self.key_system.export_key_config(target_id)

        # Add fingerprint information if available
        fingerprint_id = self.target_to_fingerprint.get(target_id)
        if fingerprint_id and fingerprint_id in self.fingerprint_manager.fingerprints:
            fp = self.fingerprint_manager.fingerprints[fingerprint_id]
            config['fingerprint'] = {
                'id': fp.id,
                'name': fp.name,
                'description': fp.description,
                'modifications': fp.modifications,
                'is_custom': fp.is_custom
            }

        return config

    def list_integrated_targets(self) -> List[Dict[str, Any]]:
        """
        List all integrated targets with fingerprints

        Returns:
            List of target dictionaries
        """
        targets = []
        for profile in self.key_system.target_profiles.values():
            fingerprint_id = self.target_to_fingerprint.get(profile.target_id)

            target_info = {
                'target_id': profile.target_id,
                'name': profile.name,
                'strategy': profile.encoding_strategy.value,
                'method': profile.key_derivation_method.value,
                'fingerprint_id': fingerprint_id
            }

            if fingerprint_id:
                fp = self.fingerprint_manager.fingerprints.get(fingerprint_id)
                if fp:
                    target_info['fingerprint_name'] = fp.name

            targets.append(target_info)

        return targets

    def generate_integration_report(self) -> str:
        """
        Generate comprehensive integration report

        Returns:
            Formatted report string
        """
        report = "=" * 80 + "\n"
        report += "FINGERPRINT-KEY INTEGRATION SYSTEM REPORT\n"
        report += "=" * 80 + "\n\n"

        report += f"Fingerprints: {len(self.fingerprint_manager.fingerprints)}\n"
        report += f"Encoding Targets: {len(self.key_system.target_profiles)}\n"
        report += f"Integrated Targets: {len(self.fingerprint_to_target)}\n\n"

        report += "INTEGRATED TARGETS:\n"
        report += "-" * 80 + "\n"

        for target_id, fp_id in self.fingerprint_to_target.items():
            profile = self.key_system.target_profiles[target_id]
            fp = self.fingerprint_manager.fingerprints[fp_id]

            report += f"\n{profile.name}\n"
            report += f"  Target ID: {target_id}\n"
            report += f"  Fingerprint: {fp.name} ({fp_id})\n"
            report += f"  Encoding Strategy: {profile.encoding_strategy.value}\n"
            report += f"  Key Derivation: {profile.key_derivation_method.value}\n"

            if target_id in self.key_system.derived_keys:
                key = self.key_system.derived_keys[target_id]
                report += f"  Key Hash: {key.fingerprint_hash[:16]}...\n"

        report += "\n" + "=" * 80 + "\n"
        return report


def demonstrate_integration():
    """Demonstration of fingerprint-key integration"""

    print("=" * 80)
    print("FINGERPRINT-KEY INTEGRATION DEMONSTRATION")
    print("=" * 80 + "\n")

    # Initialize system
    integration = FingerprintKeyIntegration()

    # Get available fingerprints
    available_fps = integration.fingerprint_manager.get_available_fingerprints()
    print(f"Available Fingerprints: {len(available_fps)}\n")

    # Register fingerprints with encoding targets
    registered_targets = []
    for i, fp_info in enumerate(available_fps[:2]):
        try:
            fp_id, target_id = integration.register_fingerprint_with_encoding(
                fingerprint_id=fp_info['id'],
                target_name=f"Encoded {fp_info['name']}",
                metadata={'index': i}
            )
            registered_targets.append((fp_id, target_id))
            print(f"Registered: {fp_info['name']} -> Target {target_id}")
        except Exception as e:
            print(f"Error registering {fp_info['name']}: {e}")

    print("\n" + "-" * 80 + "\n")

    # Encode payloads
    if registered_targets:
        test_payload = "This is a secret message"
        print(f"Test Payload: {test_payload}\n")

        for fp_id, target_id in registered_targets:
            try:
                encoded = integration.encode_payload_for_target(target_id, test_payload)

                print(f"\nTarget: {self.key_system.target_profiles[target_id].name}")
                print(f"  Strategy: {encoded.encoding_strategy}")
                print(f"  Encoded: {encoded.encoded[:64]}...")
                print(f"  Key Hash: {encoded.key_hash}")

                # Verify decode works
                decoded = integration.decode_payload_for_target(target_id, encoded.encoded)
                print(f"  Decoded Match: {decoded == test_payload}")

            except Exception as e:
                print(f"Error processing target {target_id}: {e}")

    print("\n" + "-" * 80 + "\n")

    # Generate report
    print(integration.generate_integration_report())


if __name__ == "__main__":
    demonstrate_integration()
