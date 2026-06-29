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

    def __init__(self, config_dir: str = '/tmp/sc-fingerprints'):
        self.config_dir = config_dir
        os.makedirs(config_dir, exist_ok=True)

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
        """Save proxies to disk"""
        px_file = os.path.join(self.config_dir, 'proxies.json')
        data = [asdict(px) for px in self.proxies.values()]
        with open(px_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _initialize_default_fingerprints(self):
        """Initialize default fingerprint templates"""
        defaults = [
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

        for default in defaults:
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
        """Modify PE file sections"""
        if not self._is_pe_file(content):
            return content

        try:
            # Check for PE signature
            if content[:2] == b'MZ':
                # Add random junk bytes to sections
                if config.get('add_junk'):
                    import random
                    junk = bytes(random.getrandbits(8) for _ in range(256))
                    content = content + junk

                # Modify section headers for evasion
                if config.get('randomize_names'):
                    content = self._randomize_section_names(content)

            return content
        except Exception as e:
            print(f"Error modifying PE sections: {e}")
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
        """Obfuscate import address table"""
        # Add random bytes to confuse import analysis
        import random
        if len(content) > 1000:
            insert_pos = random.randint(100, len(content) - 100)
            junk = bytes(random.getrandbits(8) for _ in range(100))
            content = content[:insert_pos] + junk + content[insert_pos:]
        return content

    def _encrypt_strings(self, content: bytes) -> bytes:
        """Apply string encryption"""
        import random
        # Rotate bytes as simple encryption
        rotation = random.randint(1, 255)
        encrypted = bytes((b + rotation) % 256 for b in content)
        return encrypted

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
