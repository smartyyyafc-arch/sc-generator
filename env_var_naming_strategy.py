#!/usr/bin/env python3
"""
Environment Variable Naming Strategy Module
Generates legitimate-looking variable names using multiple strategies
to evade detection and blend into normal system environments.
"""

import hashlib
import random
import string
import json
from typing import List, Dict, Tuple, Optional, Any
from enum import Enum
from dataclasses import dataclass
from datetime import datetime


class NamingStrategy(Enum):
    """Different strategies for generating legitimate-looking variable names"""
    SYSTEM_LEGACY = "system_legacy"           # Old Windows system vars (e.g., TEMP, WINDIR)
    COMMON_TOOLS = "common_tools"             # Popular tool prefixes (NODE_, PYTHON_, GIT_)
    BUILD_SYSTEM = "build_system"             # Build tool vars (CMAKE_, GRADLE_, MAVEN_)
    DEVELOPMENT = "development"               # Dev environment vars (DEBUG_, DEV_, TEST_)
    FRAMEWORK = "framework"                   # Popular framework vars (DJANGO_, FLASK_, REACT_)
    CONTAINER = "container"                   # Container/VM environment (DOCKER_, K8S_, PODMAN_)
    CI_CD = "ci_cd"                           # CI/CD pipeline vars (CI_, GITHUB_, GITLAB_)
    CLOUD = "cloud"                           # Cloud provider vars (AWS_, AZURE_, GCP_)
    RUNTIME = "runtime"                       # Runtime/VM vars (JAVA_, RUST_, GO_)
    HASH_BASED = "hash_based"                 # Hash-based obfuscation (deterministic)
    RANDOM_ALPHA = "random_alpha"             # Random alphanumeric strings
    MIXED_CASE = "mixed_case"                 # Random mixed case (blends with typos)
    ACRONYM = "acronym"                       # Made-up looking acronyms


@dataclass
class NamingStrategyConfig:
    """Configuration for naming strategy generator"""
    primary_strategy: NamingStrategy = NamingStrategy.COMMON_TOOLS
    fallback_strategies: List[NamingStrategy] = None
    add_version_suffix: bool = True
    add_timestamp: bool = False
    randomize_case: bool = True
    min_name_length: int = 8
    max_name_length: int = 32
    use_underscores: bool = True
    use_numbers: bool = True
    chunk_numbering: str = "sequential"  # sequential, hex, random
    separator: str = "_"
    seed: Optional[int] = None

    def __post_init__(self):
        if self.fallback_strategies is None:
            self.fallback_strategies = [
                NamingStrategy.SYSTEM_LEGACY,
                NamingStrategy.COMMON_TOOLS,
                NamingStrategy.BUILD_SYSTEM,
            ]


class EnvVarNamingStrategy:
    """Generates legitimate-looking environment variable names"""

    # Real system legacy variables
    SYSTEM_LEGACY_VARS = [
        "TEMP", "TMP", "WINDIR", "SYSTEMROOT", "HOMEDRIVE", "HOMEPATH",
        "PATHEXT", "COMSPEC", "PROCESSOR_IDENTIFIER", "USERDOMAIN",
        "USERNAME", "USERPROFILE", "ALLUSERSPROFILE", "APPDATA",
        "LOCALAPPDATA", "COMMONPROGRAMFILES", "PROGRAMFILES",
        "PROGRAMFILES_X86", "PROMPT", "DRIVERDATA", "LOGONSERVER"
    ]

    # Common tool prefixes
    COMMON_TOOL_PREFIXES = [
        "NODE_", "PYTHON_", "GIT_", "NPM_", "YARN_",
        "PIP_", "POETRY_", "RUBY_", "JAVA_", "GO_",
        "RUST_", "DOTNET_", "PERL_", "PHP_", "LUA_",
    ]

    # Build system variables
    BUILD_SYSTEM_PREFIXES = [
        "CMAKE_", "GRADLE_", "MAVEN_", "MAKE_", "ANT_",
        "BAZEL_", "SCONS_", "MESON_", "NINJA_", "BUILD_",
        "COMPILE_", "LINK_", "FLAGS_", "CONFIG_", "RELEASE_",
    ]

    # Development environment
    DEV_PREFIXES = [
        "DEBUG_", "DEV_", "TEST_", "DEVEL_", "QA_",
        "STAGING_", "PRODUCTION_", "SANDBOX_", "SIMULATION_",
        "TRACE_", "VERBOSE_", "LOG_LEVEL_", "PROFILING_",
    ]

    # Framework prefixes
    FRAMEWORK_PREFIXES = [
        "DJANGO_", "FLASK_", "REACT_", "ANGULAR_", "VUE_",
        "EXPRESS_", "FASTAPI_", "SPRING_", "RAILS_", "LARAVEL_",
        "ASTRO_", "NEXT_", "NUXT_", "SVELTE_", "REMIX_",
    ]

    # Container/VM environment
    CONTAINER_PREFIXES = [
        "DOCKER_", "K8S_", "KUBERNETES_", "PODMAN_",
        "CONTAINERD_", "VM_", "HYPERV_", "QEMU_",
    ]

    # CI/CD platforms
    CI_CD_PREFIXES = [
        "CI_", "CD_", "GITHUB_", "GITLAB_", "JENKINS_",
        "CIRCLECI_", "TRAVIS_", "DRONE_", "GITLAB_", "BITBUCKET_",
        "AZURE_", "GITHUB_ACTIONS_",
    ]

    # Cloud providers
    CLOUD_PREFIXES = [
        "AWS_", "AZURE_", "GCP_", "GCLOUD_", "HEROKU_",
        "VERCEL_", "NETLIFY_", "DIGITALOCEAN_", "LINODE_",
    ]

    # Runtime variables
    RUNTIME_PREFIXES = [
        "JAVA_", "RUST_", "GO_", "PYTHONPATH", "GOPATH",
        "RUSTFLAGS", "JVM_", "CLR_", "LLVM_", "GCC_",
    ]

    # Legitimate suffixes for variables
    COMMON_SUFFIXES = [
        "PATH", "HOME", "ADDR", "PORT", "HOST", "USER", "PASS",
        "KEY", "TOKEN", "ENDPOINT", "URL", "BASE", "CONFIG",
        "VERSION", "DEBUG", "LEVEL", "MODE", "TIMEOUT", "MAX",
        "MIN", "SIZE", "LIMIT", "CACHE", "BUFFER", "POOL",
    ]

    def __init__(self, config: Optional[NamingStrategyConfig] = None):
        """Initialize naming strategy generator"""
        self.config = config or NamingStrategyConfig()
        if self.config.seed is not None:
            random.seed(self.config.seed)
        self.generated_names: Dict[str, str] = {}
        self.strategy_history: List[Tuple[str, NamingStrategy]] = []

    def generate_name(self,
                     payload_id: str,
                     chunk_index: int = 0,
                     strategy: Optional[NamingStrategy] = None) -> str:
        """Generate a legitimate-looking variable name"""
        strategy = strategy or self.config.primary_strategy

        if strategy == NamingStrategy.SYSTEM_LEGACY:
            return self._generate_system_legacy(payload_id, chunk_index)
        elif strategy == NamingStrategy.COMMON_TOOLS:
            return self._generate_common_tools(payload_id, chunk_index)
        elif strategy == NamingStrategy.BUILD_SYSTEM:
            return self._generate_build_system(payload_id, chunk_index)
        elif strategy == NamingStrategy.DEVELOPMENT:
            return self._generate_development(payload_id, chunk_index)
        elif strategy == NamingStrategy.FRAMEWORK:
            return self._generate_framework(payload_id, chunk_index)
        elif strategy == NamingStrategy.CONTAINER:
            return self._generate_container(payload_id, chunk_index)
        elif strategy == NamingStrategy.CI_CD:
            return self._generate_ci_cd(payload_id, chunk_index)
        elif strategy == NamingStrategy.CLOUD:
            return self._generate_cloud(payload_id, chunk_index)
        elif strategy == NamingStrategy.RUNTIME:
            return self._generate_runtime(payload_id, chunk_index)
        elif strategy == NamingStrategy.HASH_BASED:
            return self._generate_hash_based(payload_id, chunk_index)
        elif strategy == NamingStrategy.RANDOM_ALPHA:
            return self._generate_random_alpha(payload_id, chunk_index)
        elif strategy == NamingStrategy.MIXED_CASE:
            return self._generate_mixed_case(payload_id, chunk_index)
        elif strategy == NamingStrategy.ACRONYM:
            return self._generate_acronym(payload_id, chunk_index)
        else:
            # Fallback to random alpha
            return self._generate_random_alpha(payload_id, chunk_index)

    def _generate_system_legacy(self, payload_id: str, chunk_index: int) -> str:
        """Generate legacy Windows system variable names"""
        # Use variations like WINDIR_CACHE, TEMP_CONFIG, etc.
        base = random.choice(self.SYSTEM_LEGACY_VARS)
        suffix = random.choice(self.COMMON_SUFFIXES)
        chunk_num = self._format_chunk_number(chunk_index)
        return f"{base}_{suffix}{chunk_num}"

    def _generate_common_tools(self, payload_id: str, chunk_index: int) -> str:
        """Generate popular tool prefix variable names"""
        prefix = random.choice(self.COMMON_TOOL_PREFIXES)
        suffix = random.choice(self.COMMON_SUFFIXES)
        chunk_num = self._format_chunk_number(chunk_index)
        return f"{prefix}{suffix}{chunk_num}"

    def _generate_build_system(self, payload_id: str, chunk_index: int) -> str:
        """Generate build system variable names"""
        prefix = random.choice(self.BUILD_SYSTEM_PREFIXES)
        suffix = random.choice(self.COMMON_SUFFIXES)
        chunk_num = self._format_chunk_number(chunk_index)
        return f"{prefix}{suffix}{chunk_num}"

    def _generate_development(self, payload_id: str, chunk_index: int) -> str:
        """Generate development environment variable names"""
        prefix = random.choice(self.DEV_PREFIXES)
        suffix = random.choice(self.COMMON_SUFFIXES)
        chunk_num = self._format_chunk_number(chunk_index)
        return f"{prefix}{suffix}{chunk_num}"

    def _generate_framework(self, payload_id: str, chunk_index: int) -> str:
        """Generate framework variable names"""
        prefix = random.choice(self.FRAMEWORK_PREFIXES)
        suffix = random.choice(self.COMMON_SUFFIXES)
        chunk_num = self._format_chunk_number(chunk_index)
        return f"{prefix}{suffix}{chunk_num}"

    def _generate_container(self, payload_id: str, chunk_index: int) -> str:
        """Generate container/VM environment variable names"""
        prefix = random.choice(self.CONTAINER_PREFIXES)
        suffix = random.choice(self.COMMON_SUFFIXES)
        chunk_num = self._format_chunk_number(chunk_index)
        return f"{prefix}{suffix}{chunk_num}"

    def _generate_ci_cd(self, payload_id: str, chunk_index: int) -> str:
        """Generate CI/CD pipeline variable names"""
        prefix = random.choice(self.CI_CD_PREFIXES)
        suffix = random.choice(self.COMMON_SUFFIXES)
        chunk_num = self._format_chunk_number(chunk_index)
        return f"{prefix}{suffix}{chunk_num}"

    def _generate_cloud(self, payload_id: str, chunk_index: int) -> str:
        """Generate cloud provider variable names"""
        prefix = random.choice(self.CLOUD_PREFIXES)
        suffix = random.choice(self.COMMON_SUFFIXES)
        chunk_num = self._format_chunk_number(chunk_index)
        return f"{prefix}{suffix}{chunk_num}"

    def _generate_runtime(self, payload_id: str, chunk_index: int) -> str:
        """Generate runtime environment variable names"""
        prefix = random.choice(self.RUNTIME_PREFIXES)
        # Runtime vars often have PYTHONPATH-style naming
        chunk_num = self._format_chunk_number(chunk_index)
        if chunk_num:
            return f"{prefix}{chunk_num}"
        return prefix

    def _generate_hash_based(self, payload_id: str, chunk_index: int) -> str:
        """Generate deterministic hash-based variable names"""
        combined = f"{payload_id}_{chunk_index}"
        hash_value = hashlib.md5(combined.encode()).hexdigest()

        # Use first 8 chars as base
        base = hash_value[:8].upper()

        # Add human-readable prefix that looks like a tool
        prefix = random.choice(self.COMMON_TOOL_PREFIXES + self.BUILD_SYSTEM_PREFIXES)

        return f"{prefix}{base}"

    def _generate_random_alpha(self, payload_id: str, chunk_index: int) -> str:
        """Generate random alphanumeric variable names"""
        chars = string.ascii_uppercase + string.digits
        length = random.randint(
            self.config.min_name_length,
            self.config.max_name_length
        )

        # Ensure starts with letter
        name = random.choice(string.ascii_uppercase)
        name += ''.join(random.choice(chars) for _ in range(length - 1))

        # Add chunk number if needed
        chunk_num = self._format_chunk_number(chunk_index)
        if chunk_num:
            name = f"{name}{self.config.separator}{chunk_num}"

        return name

    def _generate_mixed_case(self, payload_id: str, chunk_index: int) -> str:
        """Generate mixed case variable names (looks like typos)"""
        # This makes it look like someone typed a var name with accidental case changes
        base = random.choice(
            self.COMMON_TOOL_PREFIXES +
            self.BUILD_SYSTEM_PREFIXES +
            self.FRAMEWORK_PREFIXES
        ).strip("_")

        # Randomize internal case
        mixed = ''.join(
            c.upper() if random.random() > 0.5 else c.lower()
            for c in base
        )

        suffix = random.choice(self.COMMON_SUFFIXES).lower()
        chunk_num = self._format_chunk_number(chunk_index)

        return f"{mixed}{self.config.separator}{suffix}{chunk_num}".upper()

    def _generate_acronym(self, payload_id: str, chunk_index: int) -> str:
        """Generate made-up looking acronyms"""
        # Create pronounceable-ish acronyms
        vowels = "AEIOU"
        consonants = "BCDFGHJKLMNPRSTVWXYZ"

        length = random.randint(4, 8)
        acronym = ""

        for i in range(length):
            if i % 2 == 0:
                acronym += random.choice(consonants)
            else:
                acronym += random.choice(vowels)

        chunk_num = self._format_chunk_number(chunk_index)

        return f"{acronym}{self.config.separator}{chunk_num}"

    def _format_chunk_number(self, chunk_index: int) -> str:
        """Format chunk index based on configuration"""
        if chunk_index == 0 and not self.config.add_version_suffix:
            return ""

        if self.config.chunk_numbering == "sequential":
            return f"{chunk_index:03d}"
        elif self.config.chunk_numbering == "hex":
            return f"{chunk_index:02x}".upper()
        elif self.config.chunk_numbering == "random":
            return f"{random.randint(0, 9999):04d}"
        else:
            return f"{chunk_index:03d}"

    def _apply_case_randomization(self, name: str) -> str:
        """Randomly modify case (if enabled)"""
        if not self.config.randomize_case:
            return name

        result = ""
        for char in name:
            if char.isalpha() and random.random() > 0.7:
                result += char.swapcase()
            else:
                result += char

        return result

    def generate_chunk_names(self,
                            payload_id: str,
                            num_chunks: int,
                            strategy: Optional[NamingStrategy] = None) -> List[str]:
        """Generate multiple variable names for chunks"""
        strategy = strategy or self.config.primary_strategy
        names = []

        for i in range(num_chunks):
            name = self.generate_name(payload_id, i, strategy)
            names.append(name)
            self.strategy_history.append((name, strategy))

        return names

    def generate_with_rotation(self,
                              payload_id: str,
                              num_chunks: int) -> List[str]:
        """Generate names using rotation through multiple strategies"""
        strategies = [self.config.primary_strategy] + self.config.fallback_strategies
        names = []

        for i in range(num_chunks):
            strategy = strategies[i % len(strategies)]
            name = self.generate_name(payload_id, i, strategy)
            names.append(name)
            self.strategy_history.append((name, strategy))

        return names

    def get_strategy_analysis(self) -> Dict[str, Any]:
        """Analyze and report on naming strategies used"""
        strategy_counts = {}
        for name, strategy in self.strategy_history:
            strategy_counts[strategy.value] = strategy_counts.get(strategy.value, 0) + 1

        return {
            "total_names_generated": len(self.strategy_history),
            "strategy_distribution": strategy_counts,
            "primary_strategy": self.config.primary_strategy.value,
            "fallback_strategies": [s.value for s in self.config.fallback_strategies],
        }

    def validate_name(self, name: str) -> Tuple[bool, str]:
        """Validate variable name follows naming conventions"""
        # Check length
        if len(name) < self.config.min_name_length:
            return False, f"Name too short: {len(name)} < {self.config.min_name_length}"

        if len(name) > self.config.max_name_length:
            return False, f"Name too long: {len(name)} > {self.config.max_name_length}"

        # Must start with letter or underscore
        if not name[0].isalpha() and name[0] != '_':
            return False, "Must start with letter or underscore"

        # Only alphanumeric and underscore
        if not all(c.isalnum() or c == '_' for c in name):
            return False, "Contains invalid characters"

        return True, "Valid"


class MultiStrategyNamer:
    """Generates diverse variable names across multiple strategies"""

    def __init__(self, seed: Optional[int] = None):
        """Initialize multi-strategy namer"""
        self.seed = seed
        if seed is not None:
            random.seed(seed)

    def generate_diverse_set(self,
                            payload_id: str,
                            num_chunks: int,
                            num_strategies: int = 3) -> Dict[str, List[str]]:
        """Generate names using different strategies for variety"""
        strategies = random.sample(
            list(NamingStrategy),
            min(num_strategies, len(NamingStrategy))
        )

        result = {}

        for strategy in strategies:
            config = NamingStrategyConfig(primary_strategy=strategy)
            namer = EnvVarNamingStrategy(config)
            names = namer.generate_chunk_names(payload_id, num_chunks, strategy)
            result[strategy.value] = names

        return result

    def generate_recommendation(self,
                               environment: str = "generic") -> NamingStrategyConfig:
        """Generate recommended config based on target environment"""
        recommendations = {
            "generic": NamingStrategyConfig(
                primary_strategy=NamingStrategy.COMMON_TOOLS,
                fallback_strategies=[
                    NamingStrategy.BUILD_SYSTEM,
                    NamingStrategy.SYSTEM_LEGACY,
                ]
            ),
            "cloud": NamingStrategyConfig(
                primary_strategy=NamingStrategy.CLOUD,
                fallback_strategies=[
                    NamingStrategy.CI_CD,
                    NamingStrategy.CONTAINER,
                ]
            ),
            "development": NamingStrategyConfig(
                primary_strategy=NamingStrategy.DEVELOPMENT,
                fallback_strategies=[
                    NamingStrategy.COMMON_TOOLS,
                    NamingStrategy.FRAMEWORK,
                ]
            ),
            "container": NamingStrategyConfig(
                primary_strategy=NamingStrategy.CONTAINER,
                fallback_strategies=[
                    NamingStrategy.RUNTIME,
                    NamingStrategy.CI_CD,
                ]
            ),
            "ci_cd": NamingStrategyConfig(
                primary_strategy=NamingStrategy.CI_CD,
                fallback_strategies=[
                    NamingStrategy.BUILD_SYSTEM,
                    NamingStrategy.CLOUD,
                ]
            ),
            "stealthy": NamingStrategyConfig(
                primary_strategy=NamingStrategy.HASH_BASED,
                fallback_strategies=[
                    NamingStrategy.MIXED_CASE,
                    NamingStrategy.ACRONYM,
                ]
            ),
        }

        return recommendations.get(environment, recommendations["generic"])


# ============================================================================
# Demonstration and Testing
# ============================================================================

def demo_naming_strategies():
    """Demonstrate all naming strategies"""
    print("\n" + "=" * 80)
    print("ENVIRONMENT VARIABLE NAMING STRATEGY DEMONSTRATION")
    print("=" * 80)

    strategies = [
        NamingStrategy.SYSTEM_LEGACY,
        NamingStrategy.COMMON_TOOLS,
        NamingStrategy.BUILD_SYSTEM,
        NamingStrategy.DEVELOPMENT,
        NamingStrategy.FRAMEWORK,
        NamingStrategy.CONTAINER,
        NamingStrategy.CI_CD,
        NamingStrategy.CLOUD,
        NamingStrategy.RUNTIME,
        NamingStrategy.HASH_BASED,
        NamingStrategy.RANDOM_ALPHA,
        NamingStrategy.MIXED_CASE,
        NamingStrategy.ACRONYM,
    ]

    payload_id = "SECRET_PAYLOAD_001"
    num_chunks = 4

    print(f"\nGenerating {num_chunks} chunks for payload: {payload_id}\n")

    for strategy in strategies:
        config = NamingStrategyConfig(primary_strategy=strategy)
        namer = EnvVarNamingStrategy(config)
        names = namer.generate_chunk_names(payload_id, num_chunks, strategy)

        print(f"{strategy.value.upper()}")
        print("-" * 80)
        for i, name in enumerate(names):
            print(f"  Chunk {i}: {name}")
        print()


def demo_rotation_strategy():
    """Demonstrate rotation through multiple strategies"""
    print("\n" + "=" * 80)
    print("ROTATION STRATEGY (Multiple strategies for single payload)")
    print("=" * 80 + "\n")

    config = NamingStrategyConfig(
        primary_strategy=NamingStrategy.COMMON_TOOLS,
        fallback_strategies=[
            NamingStrategy.BUILD_SYSTEM,
            NamingStrategy.DEVELOPMENT,
        ]
    )

    namer = EnvVarNamingStrategy(config)
    names = namer.generate_with_rotation("PAYLOAD_ROTATION", 6)

    for i, name in enumerate(names):
        print(f"Chunk {i}: {name}")

    print("\nStrategy Analysis:")
    analysis = namer.get_strategy_analysis()
    for key, value in analysis.items():
        print(f"  {key}: {value}")


def demo_recommendation():
    """Demonstrate environment-based recommendations"""
    print("\n" + "=" * 80)
    print("ENVIRONMENT-BASED RECOMMENDATIONS")
    print("=" * 80 + "\n")

    environments = ["generic", "cloud", "development", "container", "ci_cd", "stealthy"]

    multi_namer = MultiStrategyNamer()

    for env in environments:
        print(f"\nEnvironment: {env.upper()}")
        print("-" * 80)

        config = multi_namer.generate_recommendation(env)
        print(f"Primary Strategy: {config.primary_strategy.value}")
        print(f"Fallback Strategies: {[s.value for s in config.fallback_strategies]}")

        namer = EnvVarNamingStrategy(config)
        names = namer.generate_chunk_names("PAYLOAD", 3, config.primary_strategy)
        print(f"Example names: {names}")


def demo_diverse_set():
    """Demonstrate generating diverse sets"""
    print("\n" + "=" * 80)
    print("DIVERSE SET GENERATION (Multiple strategies simultaneously)")
    print("=" * 80 + "\n")

    multi_namer = MultiStrategyNamer(seed=42)
    diverse = multi_namer.generate_diverse_set("PAYLOAD_DIVERSE", 3, 4)

    for strategy_name, names in diverse.items():
        print(f"\n{strategy_name.upper()}")
        print("-" * 80)
        for i, name in enumerate(names):
            print(f"  Chunk {i}: {name}")


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "ENV VAR NAMING STRATEGY SUITE" + " " * 30 + "║")
    print("║" + " " * 78 + "║")
    print("║" + " " * 16 + "Legitimate-looking variable names for stealth storage" + " " * 7 + "║")
    print("╚" + "=" * 78 + "╝")

    demo_naming_strategies()
    demo_rotation_strategy()
    demo_recommendation()
    demo_diverse_set()

    print("\n" + "=" * 80)
    print("DEMONSTRATION COMPLETE")
    print("=" * 80 + "\n")
