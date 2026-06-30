#!/usr/bin/env python3
"""
Fingerprint Manager - Handle fingerprinting and proxy support
For authorized pentesting and security research
"""

import hashlib
import json
import os
import uuid
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class FingerprintConfig:
    """Fingerprint configuration"""
    id: str
    name: str
    description: str
    modifications: Dict
    is_custom: bool = False


@dataclass
class ProxyConfig:
    """Proxy configuration"""
    id: str
    url: str
    type: str  # http, socks5, https
    auth: Optional[Dict] = None
    headers: Optional[Dict] = None


class FingerprintManager:
    """Manage fingerprints and proxy configurations"""

    def __init__(self, config_dir: Optional[str] = None):
        if config_dir is None:
            # Use a user-private directory under $HOME instead of world-readable /tmp
            home = os.environ.get('HOME', os.path.expanduser('~'))
            config_dir = os.path.join(home, '.sc-fingerprints')
        self.config_dir = config_dir
        os.makedirs(config_dir, mode=0o700, exist_ok=True)

        self.fingerprints: Dict[str, FingerprintConfig] = {}
        self.proxies: Dict[str, ProxyConfig] = {}

        self._load_configs()
        self._initialize_default_fingerprints()

    def _load_configs(self):
        """Load saved configurations from disk"""
        # Load fingerprints
        fp_file = os.path.join(self.config_dir, 'fingerprints.json')
        if os.path.exists(fp_file):
            try:
                with open(fp_file, 'r') as f:
                    data = json.load(f)
                    for fp_data in data:
                        fp = FingerprintConfig(**fp_data)
                        self.fingerprints[fp.id] = fp
            except Exception as e:
                print(f"Error loading fingerprints: {e}")

        # Load proxies
        px_file = os.path.join(self.config_dir, 'proxies.json')
        if os.path.exists(px_file):
            try:
                with open(px_file, 'r') as f:
                    data = json.load(f)
                    for px_data in data:
                        px = ProxyConfig(**px_data)
                        self.proxies[px.id] = px
            except Exception as e:
                print(f"Error loading proxies: {e}")

    def _save_fingerprints(self):
        """Save fingerprints to disk"""
        fp_file = os.path.join(self.config_dir, 'fingerprints.json')
        data = [asdict(fp) for fp in self.fingerprints.values()]
        with open(fp_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _save_proxies(self):
        """Save proxies to disk with restricted permissions (0o600)"""
        px_file = os.path.join(self.config_dir, 'proxies.json')
        data = [asdict(px) for px in self.proxies.values()]
        # Use os.open with explicit mode to ensure the file is never
        # world-readable, even momentarily (avoids race with open+chmod).
        fd = os.open(px_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        try:
            with os.fdopen(fd, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception:
            os.close(fd)
            raise

    # Class-level constant for default fingerprint definitions
    _DEFAULT_FINGERPRINTS = [
        {
            'name': 'Windows Update',
            'description': 'Appears as Windows Update process',
            'modifications': {
                'pe_sections': {'add_junk': True, 'randomize_names': True},
                'imports': {'obfuscate': True},
                'strings': {'encrypt': True},
                'metadata': {'version': '10.0.19041.0', 'company': 'Microsoft Corporation'}
            }
        },
        {
            'name': 'Adobe Reader',
            'description': 'Spoofs Adobe Reader process',
            'modifications': {
                'pe_sections': {'add_junk': True},
                'metadata': {'version': '21.0.0.0', 'company': 'Adobe Inc.'}
            }
        },
        {
            'name': 'Google Chrome',
            'description': 'Mimics Chrome process signature',
            'modifications': {
                'pe_sections': {'randomize_names': True},
                'metadata': {'version': '112.0.0.0', 'company': 'Google LLC'}
            }
        },
        {
            'name': 'System Process',
            'description': 'Generic system process fingerprint',
            'modifications': {
                'pe_sections': {'add_junk': True},
                'metadata': {'company': 'Microsoft Corporation'}
            }
        },
        {
            'name': 'Random Variation',
            'description': 'Randomized fingerprint (changes each generation)',
            'modifications': {
                'pe_sections': {'add_random_junk': True, 'random_names': True},
                'randomize_all': True
            }
        },
    ]

    def _initialize_default_fingerprints(self):
        """Initialize default fingerprint templates only if no defaults exist"""
        # Check if defaults already loaded (e.g. from disk)
        existing_default_names = {
            fp.name for fp in self.fingerprints.values() if not fp.is_custom
        }
        if existing_default_names:
            return

        for default in self._DEFAULT_FINGERPRINTS:
            fp_id = str(uuid.uuid4())[:8]
            fp = FingerprintConfig(
                id=fp_id,
                name=default['name'],
                description=default['description'],
                modifications=default['modifications'],
                is_custom=False
            )
            self.fingerprints[fp_id] = fp

        self._save_fingerprints()

    def create_custom_fingerprint(self, name: str, config: Dict) -> str:
        """Create a custom fingerprint"""
        fp_id = str(uuid.uuid4())[:8]
        fp = FingerprintConfig(
            id=fp_id,
            name=name,
            description=config.get('description', 'Custom fingerprint'),
            modifications=config.get('modifications', {}),
            is_custom=True
        )
        self.fingerprints[fp_id] = fp
        self._save_fingerprints()
        return fp_id

    def get_available_fingerprints(self) -> List[Dict]:
        """Get list of available fingerprints"""
        return [
            {
                'id': fp.id,
                'name': fp.name,
                'description': fp.description,
                'is_custom': fp.is_custom
            }
            for fp in self.fingerprints.values()
        ]

    def apply_fingerprint(
        self,
        file_content: bytes,
        fingerprint_id: str,
        proxy_id: Optional[str] = None
    ) -> bytes:
        """Apply fingerprint modifications to file content"""
        if fingerprint_id not in self.fingerprints:
            raise ValueError(f"Fingerprint {fingerprint_id} not found")

        fp = self.fingerprints[fingerprint_id]
        modified_content = file_content

        # Apply modifications based on fingerprint config
        mods = fp.modifications

        # Add PE section modifications
        if 'pe_sections' in mods:
            modified_content = self._modify_pe_sections(modified_content, mods['pe_sections'])

        # Add imports obfuscation
        if mods.get('imports', {}).get('obfuscate'):
            modified_content = self._obfuscate_imports(modified_content)

        # Add string encryption
        if mods.get('strings', {}).get('encrypt'):
            modified_content = self._encrypt_strings(modified_content)

        # Apply metadata modifications
        if 'metadata' in mods:
            modified_content = self._modify_metadata(modified_content, mods['metadata'])

        # If proxy is specified, use it to test/validate
        if proxy_id:
            proxy = self.proxies.get(proxy_id)
            if proxy:
                modified_content = self._apply_proxy_characteristics(modified_content, proxy)

        return modified_content

    def _modify_pe_sections(self, content: bytes, config: Dict) -> bytes:
        """Modify PE file sections (non-destructive: writes into section slack space only)"""
        if not self._is_pe_file(content):
            return content

        try:
            if content[:2] == b'MZ':
                # Fill slack space (padding) within existing sections with junk,
                # without changing the file size or corrupting actual data.
                if config.get('add_junk'):
                    content = self._fill_section_slack(content)

                # Modify section headers for evasion
                if config.get('randomize_names'):
                    content = self._randomize_section_names(content)

            return content
        except Exception as e:
            print(f"Error modifying PE sections: {e}")
            return content

    def _fill_section_slack(self, content: bytes) -> bytes:
        """Fill slack space in PE sections with junk bytes (non-destructive).

        Each PE section has a VirtualSize (actual data) and SizeOfRawData
        (aligned size on disk). The gap between them is unused slack space
        that can safely be overwritten without affecting execution.
        """
        import random
        import struct

        try:
            pe_offset = int.from_bytes(content[0x3c:0x40], 'little')
            if pe_offset + 6 > len(content):
                return content

            num_sections = struct.unpack_from('<H', content, pe_offset + 6)[0]
            optional_hdr_size = struct.unpack_from('<H', content, pe_offset + 20)[0]
            section_table_offset = pe_offset + 24 + optional_hdr_size

            data = bytearray(content)

            for i in range(num_sections):
                entry_offset = section_table_offset + i * 40
                if entry_offset + 40 > len(data):
                    break

                virtual_size = struct.unpack_from('<I', data, entry_offset + 8)[0]
                raw_size = struct.unpack_from('<I', data, entry_offset + 16)[0]
                raw_offset = struct.unpack_from('<I', data, entry_offset + 20)[0]

                if raw_size > virtual_size and raw_offset + virtual_size < len(data):
                    slack_start = raw_offset + virtual_size
                    slack_end = min(raw_offset + raw_size, len(data))
                    if slack_end > slack_start:
                        junk = bytes(random.getrandbits(8) for _ in range(slack_end - slack_start))
                        data[slack_start:slack_end] = junk

            return bytes(data)
        except Exception:
            return content

    def _randomize_section_names(self, content: bytes) -> bytes:
        """Randomize PE section names"""
        try:
            import random
            import string

            # Find PE header
            pe_offset = int.from_bytes(content[0x3c:0x40], 'little')

            # Look for common section names and randomize them
            old_names = [b'.text', b'.data', b'.rsrc', b'.reloc']
            for old_name in old_names:
                if old_name in content:
                    new_name = bytes(''.join(
                        random.choices(string.ascii_lowercase, k=len(old_name))
                    ), 'ascii')
                    content = content.replace(old_name, new_name, 1)

            return content
        except Exception as e:
            print(f"Error randomizing section names: {e}")
            return content

    def _obfuscate_imports(self, content: bytes) -> bytes:
        """Obfuscate import table by shuffling import directory entries in-place.

        Each IMAGE_IMPORT_DESCRIPTOR is a 20-byte record. We shuffle the order
        of these entries (excluding the null terminator) so that static analysis
        tools see a different import order, but the binary remains valid because
        the loader does not depend on entry order.
        """
        if not self._is_pe_file(content):
            return content

        import random
        import struct

        try:
            pe_offset = int.from_bytes(content[0x3c:0x40], 'little')
            # PE signature check
            if content[pe_offset:pe_offset + 4] != b'PE\x00\x00':
                return content

            optional_hdr_offset = pe_offset + 24
            magic = struct.unpack_from('<H', content, optional_hdr_offset)[0]

            # Determine import directory RVA location based on PE32 vs PE32+
            if magic == 0x10b:  # PE32
                import_dir_rva_offset = optional_hdr_offset + 104
            elif magic == 0x20b:  # PE32+
                import_dir_rva_offset = optional_hdr_offset + 120
            else:
                return content

            if import_dir_rva_offset + 8 > len(content):
                return content

            import_rva = struct.unpack_from('<I', content, import_dir_rva_offset)[0]
            import_size = struct.unpack_from('<I', content, import_dir_rva_offset + 4)[0]

            if import_rva == 0 or import_size < 20:
                return content

            # Convert RVA to file offset using section table
            num_sections = struct.unpack_from('<H', content, pe_offset + 6)[0]
            optional_hdr_size = struct.unpack_from('<H', content, pe_offset + 20)[0]
            section_table_offset = pe_offset + 24 + optional_hdr_size

            import_file_offset = None
            for i in range(num_sections):
                entry = section_table_offset + i * 40
                if entry + 40 > len(content):
                    break
                sec_va = struct.unpack_from('<I', content, entry + 12)[0]
                sec_raw_size = struct.unpack_from('<I', content, entry + 16)[0]
                sec_raw_offset = struct.unpack_from('<I', content, entry + 20)[0]
                if sec_va <= import_rva < sec_va + sec_raw_size:
                    import_file_offset = sec_raw_offset + (import_rva - sec_va)
                    break

            if import_file_offset is None:
                return content

            # Count import descriptors (each is 20 bytes, terminated by a null entry)
            descriptor_size = 20
            entries = []
            offset = import_file_offset
            while offset + descriptor_size <= len(content):
                entry_data = content[offset:offset + descriptor_size]
                if entry_data == b'\x00' * descriptor_size:
                    break  # null terminator
                entries.append(entry_data)
                offset += descriptor_size

            if len(entries) <= 1:
                return content  # nothing to shuffle

            # Shuffle entries in-place
            random.shuffle(entries)
            data = bytearray(content)
            for i, entry_data in enumerate(entries):
                start = import_file_offset + i * descriptor_size
                data[start:start + descriptor_size] = entry_data

            return bytes(data)
        except Exception:
            return content

    def _encrypt_strings(self, content: bytes) -> bytes:
        """Apply XOR encryption to printable ASCII strings in the .rdata section only.

        Finds the .rdata section (which holds read-only string data), locates
        contiguous runs of printable ASCII bytes (length >= 4), and XOR-encrypts
        them in-place. The PE header, code, import tables, and all other sections
        are left untouched.
        """
        if not self._is_pe_file(content):
            return content

        import random
        import struct
        import re

        try:
            pe_offset = int.from_bytes(content[0x3c:0x40], 'little')
            num_sections = struct.unpack_from('<H', content, pe_offset + 6)[0]
            optional_hdr_size = struct.unpack_from('<H', content, pe_offset + 20)[0]
            section_table_offset = pe_offset + 24 + optional_hdr_size

            # Find .rdata section
            rdata_offset = None
            rdata_size = None
            for i in range(num_sections):
                entry = section_table_offset + i * 40
                if entry + 40 > len(content):
                    break
                name = content[entry:entry + 8].rstrip(b'\x00')
                if name == b'.rdata':
                    rdata_size = struct.unpack_from('<I', content, entry + 16)[0]
                    rdata_offset = struct.unpack_from('<I', content, entry + 20)[0]
                    break

            if rdata_offset is None or rdata_size is None:
                return content  # No .rdata section found; leave binary untouched

            rdata_end = min(rdata_offset + rdata_size, len(content))
            rdata_data = content[rdata_offset:rdata_end]

            # Find printable ASCII strings (4+ chars) within .rdata
            # Pattern: contiguous bytes in 0x20-0x7E range, minimum length 4
            xor_key = random.randint(1, 255)
            data = bytearray(content)

            for match in re.finditer(rb'[\x20-\x7e]{4,}', rdata_data):
                start = rdata_offset + match.start()
                end = rdata_offset + match.end()
                for j in range(start, end):
                    data[j] = data[j] ^ xor_key

            return bytes(data)
        except Exception:
            return content

    def _modify_metadata(self, content: bytes, metadata: Dict) -> bytes:
        """Modify PE metadata"""
        if not self._is_pe_file(content):
            return content

        # In a real implementation, this would modify:
        # - Version resource
        # - Company name
        # - File description
        # - Internal name
        # etc.

        # For now, just add some random modifications
        import random
        if random.random() > 0.5:
            # Modify timestamp
            content = content[:4] + bytes(random.getrandbits(8) for _ in range(4)) + content[8:]

        return content

    def _apply_proxy_characteristics(self, content: bytes, proxy: ProxyConfig) -> bytes:
        """Apply proxy-specific fingerprint characteristics"""
        # Add characteristics that might be detected through proxy
        # This is more about the delivery mechanism

        import hashlib
        proxy_hash = hashlib.md5(proxy.url.encode()).digest()

        # Mix proxy characteristics into the file
        if len(content) > 100:
            for i in range(min(16, len(proxy_hash))):
                content = content[:50 + i] + bytes([content[50 + i] ^ proxy_hash[i]]) + content[51 + i:]

        return content

    def _is_pe_file(self, content: bytes) -> bool:
        """Check if content is a PE (Windows executable) file"""
        return len(content) > 64 and content[:2] == b'MZ'

    def add_proxy(self, url: str, proxy_type: str = 'http', auth: Optional[Dict] = None) -> str:
        """Add proxy configuration"""
        proxy_id = str(uuid.uuid4())[:8]
        proxy = ProxyConfig(
            id=proxy_id,
            url=url,
            type=proxy_type,
            auth=auth
        )
        self.proxies[proxy_id] = proxy
        self._save_proxies()
        return proxy_id

    def get_configured_proxies(self) -> List[Dict]:
        """Get configured proxies"""
        return [
            {
                'id': px.id,
                'url': px.url,
                'type': px.type,
                'has_auth': px.auth is not None
            }
            for px in self.proxies.values()
        ]

    def remove_proxy(self, proxy_id: str) -> bool:
        """Remove proxy configuration"""
        if proxy_id in self.proxies:
            del self.proxies[proxy_id]
            self._save_proxies()
            return True
        return False

    def remove_fingerprint(self, fingerprint_id: str) -> bool:
        """Remove fingerprint"""
        if fingerprint_id in self.fingerprints:
            del self.fingerprints[fingerprint_id]
            self._save_fingerprints()
            return True
        return False

    def get_fingerprint_details(self, fingerprint_id: str) -> Optional[Dict]:
        """Get detailed fingerprint information"""
        if fingerprint_id not in self.fingerprints:
            return None

        fp = self.fingerprints[fingerprint_id]
        return {
            'id': fp.id,
            'name': fp.name,
            'description': fp.description,
            'modifications': fp.modifications,
            'is_custom': fp.is_custom
        }


if __name__ == "__main__":
    # Test fingerprint manager
    mgr = FingerprintManager()

    print("Available Fingerprints:")
    for fp in mgr.get_available_fingerprints():
        print(f"  - {fp['name']} ({fp['id']})")

    print("\nAdding proxy...")
    proxy_id = mgr.add_proxy("http://proxy.example.com:8080", "http")
    print(f"Added proxy: {proxy_id}")

    print("\nConfigured Proxies:")
    for px in mgr.get_configured_proxies():
        print(f"  - {px['url']} ({px['type']})")
