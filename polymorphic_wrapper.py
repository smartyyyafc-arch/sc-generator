#!/usr/bin/env python3
"""
Polymorphic Command Obfuscation Wrapper
Dynamically changes encoding strategy per invocation
Each call generates a different encoding method while maintaining executable output
"""

import base64
import binascii
import random
import hashlib
import uuid
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import json


class PolymorphicStrategy(Enum):
    """Polymorphic encoding strategies"""
    BASE64 = "base64"
    HEX = "hex"
    XOR = "xor"
    ARRAY = "array"
    REVERSED = "reversed"
    CHUNK_ROT = "chunk_rot"
    BITSHIFT = "bitshift"
    NESTED_HYBRID = "nested_hybrid"


@dataclass
class PolymorphicConfig:
    """Configuration for polymorphic obfuscation"""
    strategies: List[PolymorphicStrategy] = None
    randomize_order: bool = True
    add_junk_code: bool = True
    chunk_size: int = 16
    rotation_factor: int = 3
    obfuscation_iterations: int = 1
    add_anti_analysis: bool = True
    output_format: str = "python"  # python, vbs, powershell, bash
    track_invocations: bool = True

    def __post_init__(self):
        if self.strategies is None:
            self.strategies = list(PolymorphicStrategy)


class InvocationTracker:
    """Tracks polymorphic invocations for analysis"""

    def __init__(self):
        self.invocations: List[Dict] = []
        self.strategy_counts: Dict[str, int] = {}

    def record(self, command: str, strategy: PolymorphicStrategy, metadata: Dict):
        """Record an invocation"""
        self.invocations.append({
            "id": str(uuid.uuid4())[:8],
            "command_hash": hashlib.md5(command.encode()).hexdigest()[:8],
            "strategy": strategy.value,
            "timestamp": len(self.invocations),
            "metadata": metadata,
        })
        self.strategy_counts[strategy.value] = self.strategy_counts.get(strategy.value, 0) + 1

    def get_stats(self) -> Dict:
        """Get invocation statistics"""
        return {
            "total_invocations": len(self.invocations),
            "strategy_distribution": self.strategy_counts,
            "unique_strategies_used": len(self.strategy_counts),
        }


class PolymorphicCommandEncoder:
    """Main polymorphic encoding wrapper"""

    def __init__(self, config: PolymorphicConfig = None):
        self.config = config or PolymorphicConfig()
        self.tracker = InvocationTracker()
        self._strategy_registry = self._initialize_strategies()

    def _initialize_strategies(self) -> Dict[PolymorphicStrategy, Callable]:
        """Initialize all encoding strategies"""
        return {
            PolymorphicStrategy.BASE64: self._encode_base64,
            PolymorphicStrategy.HEX: self._encode_hex,
            PolymorphicStrategy.XOR: self._encode_xor,
            PolymorphicStrategy.ARRAY: self._encode_array,
            PolymorphicStrategy.REVERSED: self._encode_reversed,
            PolymorphicStrategy.CHUNK_ROT: self._encode_chunk_rot,
            PolymorphicStrategy.BITSHIFT: self._encode_bitshift,
            PolymorphicStrategy.NESTED_HYBRID: self._encode_nested_hybrid,
        }

    def encode(self, command: str) -> Dict:
        """
        Main entry point: polymorphic encode with random strategy
        Each invocation selects a different strategy
        """
        # Select random strategy
        strategy = random.choice(self.config.strategies)

        # Encode with selected strategy
        encoder_func = self._strategy_registry[strategy]
        encoded_data, metadata = encoder_func(command)

        # Generate decoder for selected strategy
        decoder_code = self._generate_decoder(strategy, encoded_data, metadata)

        # Create polymorphic payload
        payload = {
            "strategy": strategy.value,
            "encoded_data": encoded_data,
            "metadata": metadata,
            "decoder_code": decoder_code,
            "decoder_name": metadata.get("decoder_name", "decode_cmd"),
            "var_name": metadata.get("var_name", "cmd"),
        }

        # Track invocation
        if self.config.track_invocations:
            self.tracker.record(command, strategy, metadata)

        return payload

    def _encode_base64(self, command: str) -> Tuple[str, Dict]:
        """Base64 encoding"""
        encoded = base64.b64encode(command.encode()).decode()
        metadata = {
            "method": "base64",
            "original_length": len(command),
            "encoded_length": len(encoded),
            "decoder_name": f"_decode_b64_{random.randint(1000, 9999)}",
            "var_name": f"_cmd_b64_{random.randint(1000, 9999)}",
        }
        return encoded, metadata

    def _encode_hex(self, command: str) -> Tuple[str, Dict]:
        """Hex encoding"""
        encoded = command.encode().hex()
        metadata = {
            "method": "hex",
            "original_length": len(command),
            "encoded_length": len(encoded),
            "decoder_name": f"_decode_hex_{random.randint(1000, 9999)}",
            "var_name": f"_cmd_hex_{random.randint(1000, 9999)}",
        }
        return encoded, metadata

    def _encode_xor(self, command: str) -> Tuple[str, Dict]:
        """XOR encoding with random key"""
        key = random.randint(1, 255)
        encoded_bytes = bytes([b ^ key for b in command.encode()])
        encoded = encoded_bytes.hex()
        metadata = {
            "method": "xor",
            "xor_key": key,
            "original_length": len(command),
            "encoded_length": len(encoded),
            "decoder_name": f"_decode_xor_{random.randint(1000, 9999)}",
            "var_name": f"_cmd_xor_{random.randint(1000, 9999)}",
        }
        return encoded, metadata

    def _encode_array(self, command: str) -> Tuple[str, Dict]:
        """Array-based chunked encoding"""
        chunks = [
            command[i:i + self.config.chunk_size]
            for i in range(0, len(command), self.config.chunk_size)
        ]
        encoded_chunks = [binascii.hexlify(c.encode()).decode() for c in chunks]
        metadata = {
            "method": "array",
            "chunks": encoded_chunks,
            "chunk_count": len(encoded_chunks),
            "decoder_name": f"_decode_arr_{random.randint(1000, 9999)}",
            "var_name": f"_cmd_arr_{random.randint(1000, 9999)}",
        }
        return "|".join(encoded_chunks), metadata

    def _encode_reversed(self, command: str) -> Tuple[str, Dict]:
        """Reversed encoding with hex"""
        hex_encoded = command.encode().hex()
        reversed_encoded = hex_encoded[::-1]
        metadata = {
            "method": "reversed",
            "original_length": len(command),
            "encoded_length": len(reversed_encoded),
            "decoder_name": f"_decode_rev_{random.randint(1000, 9999)}",
            "var_name": f"_cmd_rev_{random.randint(1000, 9999)}",
        }
        return reversed_encoded, metadata

    def _encode_chunk_rot(self, command: str) -> Tuple[str, Dict]:
        """Chunk rotation encoding"""
        rot = self.config.rotation_factor
        chunks = [
            command[i:i + self.config.chunk_size]
            for i in range(0, len(command), self.config.chunk_size)
        ]
        rotated_chunks = chunks[rot:] + chunks[:rot]
        encoded_chunks = [binascii.hexlify(c.encode()).decode() for c in rotated_chunks]
        metadata = {
            "method": "chunk_rot",
            "rotation": rot,
            "chunks": encoded_chunks,
            "decoder_name": f"_decode_rot_{random.randint(1000, 9999)}",
            "var_name": f"_cmd_rot_{random.randint(1000, 9999)}",
        }
        return "|".join(encoded_chunks), metadata

    def _encode_bitshift(self, command: str) -> Tuple[str, Dict]:
        """Bit shift encoding with modulo preservation"""
        shift = random.randint(1, 3)  # Limited shift to avoid loss of data
        # Use bitwise operations that are reversible
        encoded_bytes = bytes([((b << shift) | (b >> (8 - shift))) & 0xFF for b in command.encode()])
        encoded = encoded_bytes.hex()
        metadata = {
            "method": "bitshift",
            "shift": shift,
            "original_length": len(command),
            "encoded_length": len(encoded),
            "decoder_name": f"_decode_bs_{random.randint(1000, 9999)}",
            "var_name": f"_cmd_bs_{random.randint(1000, 9999)}",
        }
        return encoded, metadata

    def _encode_nested_hybrid(self, command: str) -> Tuple[str, Dict]:
        """Nested hybrid encoding: base64 -> hex -> reversed"""
        layer1 = base64.b64encode(command.encode()).decode()
        layer2 = layer1.encode().hex()
        layer3 = layer2[::-1]
        metadata = {
            "method": "nested_hybrid",
            "layers": ["base64", "hex", "reversed"],
            "original_length": len(command),
            "decoder_name": f"_decode_hybrid_{random.randint(1000, 9999)}",
            "var_name": f"_cmd_hybrid_{random.randint(1000, 9999)}",
        }
        return layer3, metadata

    def _generate_decoder(self, strategy: PolymorphicStrategy, encoded_data: str, metadata: Dict) -> str:
        """Generate decoder code for selected strategy"""
        decoder_name = metadata["decoder_name"]
        var_name = metadata["var_name"]

        if strategy == PolymorphicStrategy.BASE64:
            return f"""import base64
{var_name} = "{encoded_data}"
def {decoder_name}(): return base64.b64decode({var_name}).decode()
"""

        elif strategy == PolymorphicStrategy.HEX:
            return f"""{var_name} = "{encoded_data}"
def {decoder_name}(): return bytes.fromhex({var_name}).decode()
"""

        elif strategy == PolymorphicStrategy.XOR:
            key = metadata["xor_key"]
            return f"""{var_name} = "{encoded_data}"
def {decoder_name}():
    key = {key}
    return bytes([int({var_name}[i:i+2], 16) ^ key for i in range(0, len({var_name}), 2)]).decode()
"""

        elif strategy == PolymorphicStrategy.ARRAY:
            chunks = metadata["chunks"]
            chunk_list = '[' + ', '.join(f'"{c}"' for c in chunks) + ']'
            return f"""{var_name} = {chunk_list}
def {decoder_name}(): return ''.join([bytes.fromhex(c).decode() for c in {var_name}])
"""

        elif strategy == PolymorphicStrategy.REVERSED:
            return f"""{var_name} = "{encoded_data}"
def {decoder_name}():
    rev = {var_name}[::-1]
    return bytes.fromhex(rev).decode()
"""

        elif strategy == PolymorphicStrategy.CHUNK_ROT:
            rot = metadata["rotation"]
            chunks = metadata["chunks"]
            chunk_list = '[' + ', '.join(f'"{c}"' for c in chunks) + ']'
            return f"""{var_name} = {chunk_list}
def {decoder_name}():
    rot = {rot}
    chunks = {var_name}
    original = chunks[-rot:] + chunks[:-rot]
    return ''.join([bytes.fromhex(c).decode() for c in original])
"""

        elif strategy == PolymorphicStrategy.BITSHIFT:
            shift = metadata["shift"]
            return f"""{var_name} = "{encoded_data}"
def {decoder_name}():
    shift = {shift}
    encoded_bytes = bytes.fromhex({var_name})
    return bytes([((b >> shift) | (b << (8 - shift))) & 0xFF for b in encoded_bytes]).decode()
"""

        elif strategy == PolymorphicStrategy.NESTED_HYBRID:
            return f"""import base64
{var_name} = "{encoded_data}"
def {decoder_name}():
    step1 = {var_name}[::-1]
    step2 = bytes.fromhex(step1).decode()
    step3 = base64.b64decode(step2).decode()
    return step3
"""

        return ""

    def generate_wrapper_script(self, command: str, iterations: int = 1) -> str:
        """Generate polymorphic wrapper that changes encoding each iteration"""
        payloads = []
        for _ in range(iterations):
            payload = self.encode(command)
            payloads.append(payload)

        # Build wrapper
        wrapper = "#!/usr/bin/env python3\n"
        wrapper += "# Polymorphic Command Obfuscation Wrapper\n"
        wrapper += f"# Generates {iterations} different encodings per invocation\n"
        wrapper += "import base64\nimport sys\n\n"

        # Add all decoders
        for i, payload in enumerate(payloads):
            wrapper += f"# Variant {i+1}: {payload['strategy']}\n"
            wrapper += payload['decoder_code'] + "\n"

        # Add execution logic
        wrapper += "\ndef execute_polymorphic():\n"
        for i, payload in enumerate(payloads):
            decoder_name = payload['decoder_name']
            if i == 0:
                wrapper += f"    cmd = {decoder_name}()\n"
            else:
                wrapper += f"    # Fallback: cmd = {decoder_name}()\n"

        wrapper += "    import subprocess\n"
        wrapper += "    subprocess.run(cmd, shell=True)\n\n"
        wrapper += "if __name__ == '__main__':\n"
        wrapper += "    execute_polymorphic()\n"

        return wrapper

    def generate_vbs_wrapper(self, command: str, iterations: int = 1) -> str:
        """Generate VBS wrapper with polymorphic encoding"""
        payloads = []
        for _ in range(iterations):
            payload = self.encode(command)
            payloads.append(payload)

        vbs = "' Polymorphic Command Obfuscation Wrapper\n"
        vbs += f"' Generates {iterations} different encodings\n"
        vbs += "Option Explicit\n\n"

        for i, payload in enumerate(payloads):
            strategy = payload['strategy']
            encoded = payload['encoded_data']
            var_name = payload['var_name']

            vbs += f"' Variant {i+1}: {strategy}\n"

            if strategy == "base64":
                vbs += f'Dim {var_name}\n{var_name} = "{encoded}"\n'
                vbs += f'Set objXML = CreateObject("MSXML2.DOMDocument")\n'
                vbs += f'objXML.LoadXML "<u><![CDATA[" & {var_name} & "]]></u>"\n'
                vbs += f'Dim cmd: cmd = objXML.SelectSingleNode("u").text\n'

            elif strategy == "hex":
                decoder_func = f"DecodeHex_{random.randint(1000, 9999)}"
                vbs += f'Function {decoder_func}(h)\n'
                vbs += f'    Dim i, r\n'
                vbs += f'    For i = 1 To Len(h) Step 2\n'
                vbs += f'        r = r & Chr(CLng("&H" & Mid(h, i, 2)))\n'
                vbs += f'    Next\n'
                vbs += f'    {decoder_func} = r\n'
                vbs += f'End Function\n'
                vbs += f'Dim {var_name}\n{var_name} = "{encoded}"\n'
                vbs += f'Dim cmd: cmd = {decoder_func}({var_name})\n'

            vbs += "\n"

        vbs += 'Dim shell\nSet shell = CreateObject("WScript.Shell")\n'
        vbs += 'shell.Run cmd, 0, False\n'
        vbs += 'Set shell = Nothing\n'

        return vbs

    def generate_powershell_wrapper(self, command: str, iterations: int = 1) -> str:
        """Generate PowerShell wrapper with polymorphic encoding"""
        payloads = []
        for _ in range(iterations):
            payload = self.encode(command)
            payloads.append(payload)

        ps = "# Polymorphic Command Obfuscation Wrapper\n"
        ps += f"# Generates {iterations} different encodings\n\n"

        for i, payload in enumerate(payloads):
            strategy = payload['strategy']
            encoded = payload['encoded_data']
            var_name = payload['var_name']

            ps += f"# Variant {i+1}: {strategy}\n"

            if strategy == "base64":
                ps += f'$cmd = "{encoded}"\n'
                ps += f'$decoded = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($cmd))\n'

            elif strategy == "hex":
                ps += f'$cmd = "{encoded}"\n'
                ps += f'$decoded = [System.Text.Encoding]::UTF8.GetString([byte[]]@($cmd -split \'(..)\' | Where-Object {{$_}} | ForEach-Object {{[convert]::ToByte($_, 16)}}))\n'

            ps += "\n"

        ps += "Invoke-Expression $decoded\n"

        return ps

    def generate_bash_wrapper(self, command: str, iterations: int = 1) -> str:
        """Generate Bash wrapper with polymorphic encoding"""
        payloads = []
        for _ in range(iterations):
            payload = self.encode(command)
            payloads.append(payload)

        bash = "#!/bin/bash\n"
        bash += "# Polymorphic Command Obfuscation Wrapper\n"
        bash += f"# Generates {iterations} different encodings\n\n"

        for i, payload in enumerate(payloads):
            strategy = payload['strategy']
            encoded = payload['encoded_data']
            var_name = payload['var_name']

            bash += f"# Variant {i+1}: {strategy}\n"

            if strategy == "base64":
                bash += f'{var_name}="{encoded}"\n'
                bash += f'decoded_cmd=$(echo "${{{var_name}}}" | base64 -d)\n'

            elif strategy == "hex":
                bash += f'{var_name}="{encoded}"\n'
                bash += f'decoded_cmd=$(echo "${{{var_name}}}" | xxd -r -p)\n'

            bash += "\n"

        bash += "eval \"${decoded_cmd}\"\n"

        return bash

    def get_statistics(self) -> Dict:
        """Get polymorphic invocation statistics"""
        return self.tracker.get_stats()


def create_polymorphic_wrapper(
    command: str,
    output_format: str = "python",
    iterations: int = 3
) -> Dict:
    """
    Convenience function to create polymorphic wrapper

    Args:
        command: Command to obfuscate
        output_format: Target format (python, vbs, powershell, bash)
        iterations: Number of encoding variants to generate

    Returns:
        Dictionary with wrapper and metadata
    """
    config = PolymorphicConfig(output_format=output_format)
    encoder = PolymorphicCommandEncoder(config)

    if output_format == "python":
        wrapper = encoder.generate_wrapper_script(command, iterations)
    elif output_format == "vbs":
        wrapper = encoder.generate_vbs_wrapper(command, iterations)
    elif output_format == "powershell":
        wrapper = encoder.generate_powershell_wrapper(command, iterations)
    elif output_format == "bash":
        wrapper = encoder.generate_bash_wrapper(command, iterations)
    else:
        wrapper = encoder.generate_wrapper_script(command, iterations)

    return {
        "wrapper": wrapper,
        "format": output_format,
        "iterations": iterations,
        "statistics": encoder.get_statistics(),
        "command_hash": hashlib.md5(command.encode()).hexdigest()[:8],
    }


if __name__ == "__main__":
    # Example usage
    test_command = "powershell.exe -NoProfile -WindowStyle Hidden -Command Write-Host 'Polymorphic'"

    print("=" * 80)
    print("POLYMORPHIC COMMAND OBFUSCATION WRAPPER - DEMONSTRATION")
    print("=" * 80)

    # Generate Python wrapper with 3 iterations
    print("\n[*] Generating Python wrapper (3 iterations)...\n")
    result = create_polymorphic_wrapper(test_command, output_format="python", iterations=3)
    print(result["wrapper"])

    print("\n" + "=" * 80)
    print("STATISTICS")
    print("=" * 80)
    print(f"Command Hash: {result['command_hash']}")
    print(f"Iterations: {result['iterations']}")
    print(f"Statistics: {result['statistics']}")

    # Generate VBS wrapper
    print("\n" + "=" * 80)
    print("VBS WRAPPER (2 iterations)")
    print("=" * 80)
    vbs_result = create_polymorphic_wrapper(test_command, output_format="vbs", iterations=2)
    print(vbs_result["wrapper"][:500] + "...")

    # Generate PowerShell wrapper
    print("\n" + "=" * 80)
    print("POWERSHELL WRAPPER (2 iterations)")
    print("=" * 80)
    ps_result = create_polymorphic_wrapper(test_command, output_format="powershell", iterations=2)
    print(ps_result["wrapper"][:500] + "...")

    # Generate Bash wrapper
    print("\n" + "=" * 80)
    print("BASH WRAPPER (2 iterations)")
    print("=" * 80)
    bash_result = create_polymorphic_wrapper(test_command, output_format="bash", iterations=2)
    print(bash_result["wrapper"][:500] + "...")

    # Show strategy distribution
    print("\n" + "=" * 80)
    print("STRATEGY DISTRIBUTION (10 invocations)")
    print("=" * 80)
    encoder = PolymorphicCommandEncoder()
    for i in range(10):
        encoder.encode(test_command)
    stats = encoder.get_statistics()
    print(json.dumps(stats, indent=2))
