#!/usr/bin/env python3
"""
Multi-Encoding Key Derivation System
Derives unique encoding keys from system fingerprints with per-target customization
Provides deterministic and randomized key generation strategies
For authorized pentesting and security research
"""

import hashlib
import hmac
import json
import os
import random
import string
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict, field
from enum import Enum
from datetime import datetime


class KeyDerivationMethod(Enum):
    """Key derivation methods"""
    PBKDF2 = "pbkdf2"
    HKDF = "hkdf"
    BCRYPT = "bcrypt"
    ARGON2 = "argon2"
    SCRYPT = "scrypt"
    SHA256_CHAIN = "sha256_chain"
    HMAC_CHAIN = "hmac_chain"


class EncodingStrategy(Enum):
    """Encoding strategy per target"""
    HEX = "hex"
    BASE64 = "base64"
    ROT13 = "rot13"
    XOR = "xor"
    OCTAL = "octal"
    ASCII = "ascii"
    REVERSE = "reverse"
    CUSTOM_SUBSTITUTION = "custom_substitution"


@dataclass
class FingerprintComponent:
    """Individual fingerprint component"""
    name: str
    value: str
    weight: int = 1  # Influence on key derivation


@dataclass
class TargetProfile:
    """Target-specific encoding profile"""
    target_id: str
    name: str
    fingerprint_data: Dict[str, str]
    encoding_strategy: EncodingStrategy
    key_derivation_method: KeyDerivationMethod
    salt: str = ""
    iterations: int = 100000
    key_length: int = 32
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class DerivedKey:
    """Derived encryption key with metadata"""
    key: bytes
    hex_key: str
    strategy: EncodingStrategy
    derivation_method: KeyDerivationMethod
    target_id: str
    fingerprint_hash: str
    salt_used: str
    iterations: int
    metadata: Dict[str, Any] = field(default_factory=dict)


class FingerprintHasher:
    """Generates consistent hashes from fingerprint data"""

    @staticmethod
    def hash_fingerprint(fingerprint_data: Dict[str, str], method: str = "sha256") -> str:
        """
        Generate deterministic hash from fingerprint components

        Args:
            fingerprint_data: Dictionary of fingerprint components
            method: Hash method (sha256, sha512, md5)

        Returns:
            Hex-encoded hash string
        """
        # Sort keys for consistency
        sorted_data = json.dumps(fingerprint_data, sort_keys=True).encode()

        if method == "sha256":
            return hashlib.sha256(sorted_data).hexdigest()
        elif method == "sha512":
            return hashlib.sha512(sorted_data).hexdigest()
        elif method == "md5":
            return hashlib.md5(sorted_data).hexdigest()
        else:
            return hashlib.sha256(sorted_data).hexdigest()

    @staticmethod
    def hash_with_weights(fingerprint_data: Dict[str, str], weights: Dict[str, int]) -> str:
        """
        Generate weighted hash from fingerprint components

        Args:
            fingerprint_data: Dictionary of fingerprint components
            weights: Weight multipliers for each component

        Returns:
            Hex-encoded hash string
        """
        weighted_str = ""
        for key in sorted(fingerprint_data.keys()):
            value = fingerprint_data[key]
            weight = weights.get(key, 1)
            # Repeat value according to weight
            weighted_str += (value * weight)

        return hashlib.sha256(weighted_str.encode()).hexdigest()

    @staticmethod
    def extract_components(fingerprint_hash: str, num_components: int) -> List[str]:
        """
        Extract multiple components from a fingerprint hash

        Args:
            fingerprint_hash: Hex-encoded hash string
            num_components: Number of components to extract

        Returns:
            List of hex string components
        """
        components = []
        chunk_size = len(fingerprint_hash) // num_components

        for i in range(num_components):
            start = i * chunk_size
            end = start + chunk_size if i < num_components - 1 else len(fingerprint_hash)
            components.append(fingerprint_hash[start:end])

        return components


class KeyDerivationFactory:
    """Factory for creating derived keys using various methods"""

    @staticmethod
    def derive_pbkdf2(
        fingerprint_data: Dict[str, str],
        salt: str,
        iterations: int = 100000,
        key_length: int = 32
    ) -> bytes:
        """
        Derive key using PBKDF2

        Args:
            fingerprint_data: Fingerprint data dictionary
            salt: Salt string
            iterations: Number of iterations
            key_length: Desired key length in bytes

        Returns:
            Derived key bytes
        """
        import hashlib

        fp_hash = FingerprintHasher.hash_fingerprint(fingerprint_data)
        password = (fp_hash + salt).encode()
        salt_bytes = salt.encode()

        return hashlib.pbkdf2_hmac(
            'sha256',
            password,
            salt_bytes,
            iterations,
            dklen=key_length
        )

    @staticmethod
    def derive_hkdf(
        fingerprint_data: Dict[str, str],
        salt: str,
        info: str = "multi-encoding-key",
        key_length: int = 32
    ) -> bytes:
        """
        Derive key using HKDF (HMAC-based KDF)

        Args:
            fingerprint_data: Fingerprint data dictionary
            salt: Salt string
            info: Additional info string
            key_length: Desired key length in bytes

        Returns:
            Derived key bytes
        """
        from hashlib import sha256

        # Extract phase
        fp_hash = FingerprintHasher.hash_fingerprint(fingerprint_data)
        ikm = fp_hash.encode()
        salt_bytes = salt.encode() if salt else b'\x00' * 32

        prk = hmac.new(salt_bytes, ikm, sha256).digest()

        # Expand phase
        info_bytes = info.encode()
        okm = b""
        counter = 1

        while len(okm) < key_length:
            okm += hmac.new(prk, okm[-32:] + info_bytes + bytes([counter]), sha256).digest()
            counter += 1

        return okm[:key_length]

    @staticmethod
    def derive_sha256_chain(
        fingerprint_data: Dict[str, str],
        salt: str,
        iterations: int = 100000,
        key_length: int = 32
    ) -> bytes:
        """
        Derive key using chained SHA256 hashing

        Args:
            fingerprint_data: Fingerprint data dictionary
            salt: Salt string
            iterations: Number of iterations
            key_length: Desired key length in bytes

        Returns:
            Derived key bytes
        """
        fp_hash = FingerprintHasher.hash_fingerprint(fingerprint_data)
        current = (fp_hash + salt).encode()

        for _ in range(iterations):
            current = hashlib.sha256(current).digest()

        # Expand if needed
        result = current
        while len(result) < key_length:
            result += hashlib.sha256(result).digest()

        return result[:key_length]

    @staticmethod
    def derive_hmac_chain(
        fingerprint_data: Dict[str, str],
        salt: str,
        iterations: int = 100000,
        key_length: int = 32
    ) -> bytes:
        """
        Derive key using chained HMAC operations

        Args:
            fingerprint_data: Fingerprint data dictionary
            salt: Salt string
            iterations: Number of iterations
            key_length: Desired key length in bytes

        Returns:
            Derived key bytes
        """
        fp_hash = FingerprintHasher.hash_fingerprint(fingerprint_data)
        salt_bytes = salt.encode()

        current = fp_hash.encode()
        for _ in range(iterations):
            current = hmac.new(salt_bytes, current, hashlib.sha256).digest()

        # Expand if needed
        result = current
        while len(result) < key_length:
            result = hmac.new(salt_bytes, result, hashlib.sha256).digest()

        return result[:key_length]

    @staticmethod
    def derive_bcrypt(
        fingerprint_data: Dict[str, str],
        salt: str,
        rounds: int = 12
    ) -> bytes:
        """
        Derive key using bcrypt

        Args:
            fingerprint_data: Fingerprint data dictionary
            salt: Salt string
            rounds: Number of rounds

        Returns:
            Derived key bytes
        """
        try:
            import bcrypt
            fp_hash = FingerprintHasher.hash_fingerprint(fingerprint_data)
            password = (fp_hash + salt).encode()
            hashed = bcrypt.hashpw(password, bcrypt.gensalt(rounds=rounds))
            return hashed[:32]
        except ImportError:
            # Fallback to SHA256 chain if bcrypt not available
            return KeyDerivationFactory.derive_sha256_chain(
                fingerprint_data, salt, 12 * 8192
            )

    @staticmethod
    def derive_argon2(
        fingerprint_data: Dict[str, str],
        salt: str,
        time_cost: int = 2,
        memory_cost: int = 65536,
        parallelism: int = 1,
        key_length: int = 32
    ) -> bytes:
        """
        Derive key using Argon2

        Args:
            fingerprint_data: Fingerprint data dictionary
            salt: Salt string
            time_cost: Time cost parameter
            memory_cost: Memory cost parameter
            parallelism: Parallelism parameter
            key_length: Desired key length in bytes

        Returns:
            Derived key bytes
        """
        try:
            from argon2 import PasswordHasher
            from argon2.low_level import hash_secret

            fp_hash = FingerprintHasher.hash_fingerprint(fingerprint_data)
            password = (fp_hash + salt).encode()
            salt_bytes = salt.encode()[:16].ljust(16, b'\x00')

            hashed = hash_secret(
                password,
                salt_bytes,
                time_cost=time_cost,
                memory_cost=memory_cost,
                parallelism=parallelism,
                hash_len=key_length,
                type=2  # Argon2id
            )
            return hashed[:key_length]
        except ImportError:
            # Fallback to PBKDF2 if argon2 not available
            return KeyDerivationFactory.derive_pbkdf2(
                fingerprint_data, salt, time_cost * memory_cost, key_length
            )

    @staticmethod
    def derive_scrypt(
        fingerprint_data: Dict[str, str],
        salt: str,
        n: int = 16384,
        r: int = 8,
        p: int = 1,
        key_length: int = 32
    ) -> bytes:
        """
        Derive key using Scrypt

        Args:
            fingerprint_data: Fingerprint data dictionary
            salt: Salt string
            n: CPU/memory cost parameter
            r: Block size parameter
            p: Parallelization parameter
            key_length: Desired key length in bytes

        Returns:
            Derived key bytes
        """
        try:
            from Crypto.Protocol.KDF import scrypt
            fp_hash = FingerprintHasher.hash_fingerprint(fingerprint_data)
            password = (fp_hash + salt).encode()
            salt_bytes = salt.encode()

            return scrypt(password, salt_bytes, key_length, N=n, r=r, p=p)
        except ImportError:
            # Fallback to PBKDF2 if scrypt not available
            return KeyDerivationFactory.derive_pbkdf2(
                fingerprint_data, salt, n, key_length
            )

    @staticmethod
    def derive_key(
        fingerprint_data: Dict[str, str],
        method: KeyDerivationMethod,
        salt: str = "",
        iterations: int = 100000,
        key_length: int = 32
    ) -> bytes:
        """
        Derive key using specified method

        Args:
            fingerprint_data: Fingerprint data dictionary
            method: Key derivation method
            salt: Salt string
            iterations: Number of iterations
            key_length: Desired key length in bytes

        Returns:
            Derived key bytes
        """
        if not salt:
            salt = hashlib.sha256(json.dumps(fingerprint_data, sort_keys=True).encode()).hexdigest()[:16]

        if method == KeyDerivationMethod.PBKDF2:
            return KeyDerivationFactory.derive_pbkdf2(
                fingerprint_data, salt, iterations, key_length
            )
        elif method == KeyDerivationMethod.HKDF:
            return KeyDerivationFactory.derive_hkdf(
                fingerprint_data, salt, key_length=key_length
            )
        elif method == KeyDerivationMethod.SHA256_CHAIN:
            return KeyDerivationFactory.derive_sha256_chain(
                fingerprint_data, salt, iterations, key_length
            )
        elif method == KeyDerivationMethod.HMAC_CHAIN:
            return KeyDerivationFactory.derive_hmac_chain(
                fingerprint_data, salt, iterations, key_length
            )
        elif method == KeyDerivationMethod.BCRYPT:
            return KeyDerivationFactory.derive_bcrypt(
                fingerprint_data, salt, iterations // 8192
            )
        elif method == KeyDerivationMethod.ARGON2:
            return KeyDerivationFactory.derive_argon2(
                fingerprint_data, salt, time_cost=iterations // 8192, key_length=key_length
            )
        elif method == KeyDerivationMethod.SCRYPT:
            return KeyDerivationFactory.derive_scrypt(
                fingerprint_data, salt, n=iterations, key_length=key_length
            )
        else:
            return KeyDerivationFactory.derive_sha256_chain(
                fingerprint_data, salt, iterations, key_length
            )


class EncodingStrategySelector:
    """Selects and customizes encoding strategies per target"""

    @staticmethod
    def select_strategy_from_fingerprint(
        fingerprint_data: Dict[str, str],
        available_strategies: Optional[List[EncodingStrategy]] = None
    ) -> EncodingStrategy:
        """
        Select encoding strategy based on fingerprint characteristics

        Args:
            fingerprint_data: Fingerprint data dictionary
            available_strategies: List of available strategies to choose from

        Returns:
            Selected EncodingStrategy
        """
        if available_strategies is None:
            available_strategies = list(EncodingStrategy)

        # Use fingerprint hash to deterministically select strategy
        fp_hash = FingerprintHasher.hash_fingerprint(fingerprint_data)
        strategy_index = int(fp_hash, 16) % len(available_strategies)

        return available_strategies[strategy_index]

    @staticmethod
    def get_strategy_parameters(strategy: EncodingStrategy, key: bytes) -> Dict[str, Any]:
        """
        Get encoding parameters for strategy

        Args:
            strategy: Encoding strategy
            key: Derived key bytes

        Returns:
            Dictionary of parameters for the strategy
        """
        key_int = int.from_bytes(key, 'big')

        if strategy == EncodingStrategy.XOR:
            return {
                'key': key_int % 256,
                'multi_byte': key_int % 2 == 1
            }
        elif strategy == EncodingStrategy.ROT13:
            return {
                'rotation': (key_int % 13) + 1
            }
        elif strategy == EncodingStrategy.CUSTOM_SUBSTITUTION:
            # Generate substitution table from key
            random.seed(key_int % (2**31))
            charset = string.ascii_letters + string.digits + string.punctuation
            shuffled = list(charset)
            random.shuffle(shuffled)
            return {
                'substitution_table': dict(zip(charset, shuffled))
            }
        else:
            return {'key': key}


class MultiEncodingKeySystem:
    """Main system for managing multi-encoding key derivation"""

    def __init__(self, config_dir: str = '/tmp/sc-encoding-keys'):
        """
        Initialize multi-encoding key system

        Args:
            config_dir: Directory for storing configurations
        """
        self.config_dir = config_dir
        os.makedirs(config_dir, exist_ok=True)

        self.target_profiles: Dict[str, TargetProfile] = {}
        self.derived_keys: Dict[str, DerivedKey] = {}
        self.fingerprint_hasher = FingerprintHasher()

        self._load_profiles()

    def _load_profiles(self):
        """Load saved target profiles"""
        profiles_file = os.path.join(self.config_dir, 'target_profiles.json')
        if os.path.exists(profiles_file):
            try:
                with open(profiles_file, 'r') as f:
                    data = json.load(f)
                    for profile_data in data:
                        profile = TargetProfile(
                            target_id=profile_data['target_id'],
                            name=profile_data['name'],
                            fingerprint_data=profile_data['fingerprint_data'],
                            encoding_strategy=EncodingStrategy(profile_data['encoding_strategy']),
                            key_derivation_method=KeyDerivationMethod(profile_data['key_derivation_method']),
                            salt=profile_data.get('salt', ''),
                            iterations=profile_data.get('iterations', 100000),
                            key_length=profile_data.get('key_length', 32),
                            metadata=profile_data.get('metadata', {})
                        )
                        self.target_profiles[profile.target_id] = profile
            except Exception as e:
                print(f"Error loading profiles: {e}")

    def _save_profiles(self):
        """Save target profiles"""
        profiles_file = os.path.join(self.config_dir, 'target_profiles.json')
        data = []
        for profile in self.target_profiles.values():
            profile_dict = asdict(profile)
            profile_dict['encoding_strategy'] = profile.encoding_strategy.value
            profile_dict['key_derivation_method'] = profile.key_derivation_method.value
            data.append(profile_dict)

        with open(profiles_file, 'w') as f:
            json.dump(data, f, indent=2)

    def create_target_profile(
        self,
        name: str,
        fingerprint_data: Dict[str, str],
        encoding_strategy: Optional[EncodingStrategy] = None,
        key_derivation_method: Optional[KeyDerivationMethod] = None,
        salt: str = "",
        iterations: int = 100000,
        key_length: int = 32,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TargetProfile:
        """
        Create a new target profile

        Args:
            name: Target name
            fingerprint_data: Fingerprint data dictionary
            encoding_strategy: Encoding strategy (auto-select if None)
            key_derivation_method: Key derivation method (defaults to PBKDF2)
            salt: Salt string
            iterations: Number of iterations for key derivation
            key_length: Desired key length
            metadata: Additional metadata

        Returns:
            Created TargetProfile
        """
        target_id = hashlib.md5(json.dumps(fingerprint_data, sort_keys=True).encode()).hexdigest()[:12]

        if encoding_strategy is None:
            encoding_strategy = EncodingStrategySelector.select_strategy_from_fingerprint(
                fingerprint_data
            )

        if key_derivation_method is None:
            key_derivation_method = KeyDerivationMethod.PBKDF2

        profile = TargetProfile(
            target_id=target_id,
            name=name,
            fingerprint_data=fingerprint_data,
            encoding_strategy=encoding_strategy,
            key_derivation_method=key_derivation_method,
            salt=salt,
            iterations=iterations,
            key_length=key_length,
            metadata=metadata or {}
        )

        self.target_profiles[target_id] = profile
        self._save_profiles()

        return profile

    def derive_key_for_target(
        self,
        target_id: str,
        custom_salt: Optional[str] = None
    ) -> DerivedKey:
        """
        Derive key for a specific target

        Args:
            target_id: Target identifier
            custom_salt: Override salt value

        Returns:
            DerivedKey object
        """
        if target_id not in self.target_profiles:
            raise ValueError(f"Target {target_id} not found")

        profile = self.target_profiles[target_id]

        salt = custom_salt or profile.salt
        if not salt:
            salt = hashlib.sha256(
                json.dumps(profile.fingerprint_data, sort_keys=True).encode()
            ).hexdigest()[:16]

        # Derive key using configured method
        key_bytes = KeyDerivationFactory.derive_key(
            profile.fingerprint_data,
            profile.key_derivation_method,
            salt=salt,
            iterations=profile.iterations,
            key_length=profile.key_length
        )

        fingerprint_hash = FingerprintHasher.hash_fingerprint(profile.fingerprint_data)

        derived_key = DerivedKey(
            key=key_bytes,
            hex_key=key_bytes.hex(),
            strategy=profile.encoding_strategy,
            derivation_method=profile.key_derivation_method,
            target_id=target_id,
            fingerprint_hash=fingerprint_hash,
            salt_used=salt,
            iterations=profile.iterations,
            metadata={
                'profile_name': profile.name,
                'generated_at': datetime.now().isoformat()
            }
        )

        self.derived_keys[target_id] = derived_key
        return derived_key

    def get_encoding_parameters(self, target_id: str) -> Dict[str, Any]:
        """
        Get encoding parameters for target

        Args:
            target_id: Target identifier

        Returns:
            Dictionary of encoding parameters
        """
        if target_id not in self.derived_keys:
            self.derive_key_for_target(target_id)

        derived_key = self.derived_keys[target_id]
        strategy = derived_key.strategy

        return EncodingStrategySelector.get_strategy_parameters(strategy, derived_key.key)

    def list_target_profiles(self) -> List[Dict[str, Any]]:
        """
        List all target profiles

        Returns:
            List of target profile dictionaries
        """
        return [
            {
                'target_id': profile.target_id,
                'name': profile.name,
                'strategy': profile.encoding_strategy.value,
                'method': profile.key_derivation_method.value,
                'created_at': profile.created_at
            }
            for profile in self.target_profiles.values()
        ]

    def export_key_config(self, target_id: str) -> Dict[str, Any]:
        """
        Export complete key configuration for target

        Args:
            target_id: Target identifier

        Returns:
            Complete configuration dictionary
        """
        if target_id not in self.derived_keys:
            self.derive_key_for_target(target_id)

        profile = self.target_profiles[target_id]
        derived_key = self.derived_keys[target_id]

        # Get parameters and convert bytes to hex if needed
        params = self.get_encoding_parameters(target_id)
        params_serializable = {}
        for k, v in params.items():
            if isinstance(v, bytes):
                params_serializable[k] = v.hex()
            elif isinstance(v, dict) and any(isinstance(val, bytes) for val in v.values()):
                # Handle nested bytes in dictionaries
                params_serializable[k] = {
                    sub_k: sub_v.hex() if isinstance(sub_v, bytes) else sub_v
                    for sub_k, sub_v in v.items()
                }
            else:
                params_serializable[k] = v

        return {
            'target': {
                'id': target_id,
                'name': profile.name,
                'fingerprint': profile.fingerprint_data
            },
            'key': {
                'hex': derived_key.hex_key,
                'length': len(derived_key.key),
                'derivation_method': derived_key.derivation_method.value,
                'salt': derived_key.salt_used,
                'iterations': derived_key.iterations,
                'fingerprint_hash': derived_key.fingerprint_hash
            },
            'encoding': {
                'strategy': derived_key.strategy.value,
                'parameters': params_serializable
            },
            'metadata': {
                **profile.metadata,
                **derived_key.metadata
            }
        }

    def generate_system_report(self) -> str:
        """
        Generate comprehensive system report

        Returns:
            Formatted report string
        """
        report = "=" * 80 + "\n"
        report += "MULTI-ENCODING KEY DERIVATION SYSTEM REPORT\n"
        report += "=" * 80 + "\n\n"

        report += f"Total Target Profiles: {len(self.target_profiles)}\n"
        report += f"Derived Keys: {len(self.derived_keys)}\n"
        report += f"Config Directory: {self.config_dir}\n\n"

        report += "TARGET PROFILES:\n"
        report += "-" * 80 + "\n"

        for profile in self.target_profiles.values():
            report += f"\nTarget: {profile.name} ({profile.target_id})\n"
            report += f"  Encoding Strategy: {profile.encoding_strategy.value}\n"
            report += f"  Key Derivation: {profile.key_derivation_method.value}\n"
            report += f"  Key Length: {profile.key_length} bytes\n"
            report += f"  Iterations: {profile.iterations}\n"
            report += f"  Fingerprint Components: {len(profile.fingerprint_data)}\n"

            if profile.target_id in self.derived_keys:
                key = self.derived_keys[profile.target_id]
                report += f"  Derived Key Hash: {key.fingerprint_hash[:16]}...\n"

        report += "\n" + "=" * 80 + "\n"
        return report


def demonstrate_multi_encoding_key_system():
    """Demonstration of the multi-encoding key derivation system"""

    print("=" * 80)
    print("MULTI-ENCODING KEY DERIVATION SYSTEM DEMONSTRATION")
    print("=" * 80 + "\n")

    # Initialize system
    key_system = MultiEncodingKeySystem()

    # Create example fingerprints from different systems
    fingerprints = [
        {
            'name': 'Windows Server',
            'data': {
                'os': 'Windows Server 2019',
                'processor': 'Intel Core i7',
                'hostname': 'SERVER-001',
                'domain': 'CORP',
                'version': '10.0.17763'
            }
        },
        {
            'name': 'Linux Server',
            'data': {
                'os': 'Ubuntu 20.04 LTS',
                'kernel': '5.10.0-8-generic',
                'hostname': 'web-server-01',
                'arch': 'x86_64',
                'cpu_count': '8'
            }
        },
        {
            'name': 'macOS Workstation',
            'data': {
                'os': 'macOS Big Sur',
                'version': '11.6.1',
                'model': 'MacBook Pro',
                'processor': 'Apple M1',
                'serialnumber': 'ABC123XYZ'
            }
        }
    ]

    # Create profiles for each fingerprint
    profiles = []
    for fp_info in fingerprints:
        profile = key_system.create_target_profile(
            name=fp_info['name'],
            fingerprint_data=fp_info['data']
        )
        profiles.append(profile)
        print(f"Created profile for {fp_info['name']}: {profile.target_id}")

    print("\n" + "-" * 80 + "\n")

    # Derive keys for each target
    print("DERIVED KEYS FOR EACH TARGET:\n")

    for profile in profiles:
        derived_key = key_system.derive_key_for_target(profile.target_id)

        print(f"\nTarget: {profile.name}")
        print(f"  Strategy: {derived_key.strategy.value}")
        print(f"  Method: {derived_key.derivation_method.value}")
        print(f"  Key (hex): {derived_key.hex_key}")
        print(f"  Salt: {derived_key.salt_used}")
        print(f"  Fingerprint Hash: {derived_key.fingerprint_hash[:32]}...")

    print("\n" + "-" * 80 + "\n")

    # Show encoding parameters
    print("ENCODING PARAMETERS:\n")

    for profile in profiles:
        params = key_system.get_encoding_parameters(profile.target_id)
        print(f"\n{profile.name}:")
        print(f"  Parameters: {params}")

    print("\n" + "-" * 80 + "\n")

    # Generate full report
    print(key_system.generate_system_report())

    # Export complete configuration
    print("\nEXPORTED CONFIGURATION (First Target):\n")
    config = key_system.export_key_config(profiles[0].target_id)
    print(json.dumps(config, indent=2))


if __name__ == "__main__":
    demonstrate_multi_encoding_key_system()
