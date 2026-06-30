#!/usr/bin/env python3
"""
Fingerprint Manager - Handle fingerprinting and proxy support
For authorized pentesting and security research
"""

import hashlib
import json
import os
import uuid
import platform
import psutil
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict, field


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


@dataclass
class OSFingerprint:
    """Operating System fingerprint data"""
    os_name: str
    os_version: str
    architecture: str
    processor_name: str
    processor_count: int
    processor_freq: float  # MHz
    total_memory: int  # bytes
    network_adapters: List[Dict] = field(default_factory=list)
    disk_info: Dict = field(default_factory=dict)
    python_version: str = ""
    hostname: str = ""
    timestamp: str = ""


@dataclass
class SystemHardware:
    """System hardware details"""
    cpu_model: str
    cpu_cores: int
    cpu_threads: int
    cpu_frequency_mhz: float
    ram_total_gb: float
    ram_available_gb: float
    network_interfaces: List[Dict] = field(default_factory=list)


class FingerprintManager:
    """Manage fingerprints and proxy configurations"""

    def __init__(self, config_dir: str = '/tmp/sc-fingerprints'):
        self.config_dir = config_dir
        os.makedirs(config_dir, exist_ok=True)

        self.fingerprints: Dict[str, FingerprintConfig] = {}
        self.proxies: Dict[str, ProxyConfig] = {}
        self.os_fingerprint: Optional[OSFingerprint] = None
        self.system_hardware: Optional[SystemHardware] = None

        self._load_configs()
        self._initialize_default_fingerprints()
        self._collect_system_fingerprint()

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

    def _collect_system_fingerprint(self) -> None:
        """Collect comprehensive OS and hardware fingerprint"""
        try:
            import sys
            from datetime import datetime

            # Collect basic OS information
            os_name = platform.system()
            os_version = platform.release()
            architecture = platform.machine()
            processor_name = platform.processor()
            processor_count = os.cpu_count() or 1
            processor_freq = self._get_cpu_frequency()

            # Get memory info
            try:
                total_memory = psutil.virtual_memory().total
            except AttributeError:
                total_memory = 0

            # Collect network adapter information
            network_adapters = self._collect_network_adapters()

            # Collect disk information
            disk_info = self._collect_disk_info()

            # Create OS fingerprint
            self.os_fingerprint = OSFingerprint(
                os_name=os_name,
                os_version=os_version,
                architecture=architecture,
                processor_name=processor_name,
                processor_count=processor_count,
                processor_freq=processor_freq,
                total_memory=total_memory,
                network_adapters=network_adapters,
                disk_info=disk_info,
                python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                hostname=platform.node(),
                timestamp=datetime.now().isoformat()
            )

            # Collect system hardware details
            self.system_hardware = SystemHardware(
                cpu_model=self._get_cpu_model(),
                cpu_cores=self._get_cpu_cores(),
                cpu_threads=self._get_cpu_threads(),
                cpu_frequency_mhz=processor_freq,
                ram_total_gb=total_memory / (1024**3) if total_memory > 0 else 0,
                ram_available_gb=self._get_available_memory(),
                network_interfaces=network_adapters
            )

        except Exception as e:
            print(f"Error collecting system fingerprint: {e}")

    def _get_cpu_frequency(self) -> float:
        """Get CPU frequency in MHz"""
        try:
            freq = psutil.cpu_freq()
            if freq:
                return freq.current
        except Exception:
            pass

        # Fallback: try to parse from /proc/cpuinfo on Linux
        try:
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if line.startswith('cpu MHz'):
                        return float(line.split(':')[1].strip())
        except Exception:
            pass

        return 0.0

    def _get_cpu_model(self) -> str:
        """Get CPU model name"""
        try:
            import subprocess
            if platform.system() == 'Windows':
                result = subprocess.run(
                    ['wmic', 'cpu', 'get', 'name'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    return lines[1].strip()
            elif platform.system() == 'Darwin':  # macOS
                result = subprocess.run(
                    ['sysctl', '-n', 'machdep.cpu.brand_string'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                return result.stdout.strip()
            else:  # Linux
                try:
                    with open('/proc/cpuinfo', 'r') as f:
                        for line in f:
                            if line.startswith('model name'):
                                return line.split(':')[1].strip()
                except Exception:
                    pass
        except Exception:
            pass

        return platform.processor()

    def _get_cpu_cores(self) -> int:
        """Get physical CPU cores"""
        try:
            return psutil.cpu_count(logical=False) or os.cpu_count() or 1
        except Exception:
            return os.cpu_count() or 1

    def _get_cpu_threads(self) -> int:
        """Get logical CPU threads"""
        try:
            return psutil.cpu_count(logical=True) or os.cpu_count() or 1
        except Exception:
            return os.cpu_count() or 1

    def _get_available_memory(self) -> float:
        """Get available RAM in GB"""
        try:
            available = psutil.virtual_memory().available
            return available / (1024**3)
        except Exception:
            return 0.0

    def _collect_network_adapters(self) -> List[Dict]:
        """Collect network adapter information"""
        adapters = []
        try:
            if_addrs = psutil.net_if_addrs()
            if_stats = psutil.net_if_stats()

            for interface_name, interface_addrs in if_addrs.items():
                adapter_info = {
                    'name': interface_name,
                    'addresses': [],
                    'status': 'up' if if_stats.get(interface_name, None) and if_stats[interface_name].isup else 'down',
                    'speed_mbps': 0
                }

                for addr in interface_addrs:
                    adapter_info['addresses'].append({
                        'family': str(addr.family),
                        'address': addr.address,
                        'netmask': addr.netmask,
                        'broadcast': addr.broadcast
                    })

                # Get speed if available
                if interface_name in if_stats:
                    adapter_info['speed_mbps'] = if_stats[interface_name].speed

                adapters.append(adapter_info)

        except Exception as e:
            print(f"Error collecting network adapters: {e}")

        return adapters

    def _collect_disk_info(self) -> Dict:
        """Collect disk information"""
        disk_info = {}
        try:
            partitions = psutil.disk_partitions()
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info[partition.device] = {
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total_gb': usage.total / (1024**3),
                        'used_gb': usage.used / (1024**3),
                        'free_gb': usage.free / (1024**3),
                        'percent_used': usage.percent
                    }
                except Exception:
                    pass
        except Exception as e:
            print(f"Error collecting disk info: {e}")

        return disk_info

    def get_os_fingerprint(self) -> Optional[Dict]:
        """Get collected OS fingerprint"""
        if not self.os_fingerprint:
            return None

        return {
            'os_name': self.os_fingerprint.os_name,
            'os_version': self.os_fingerprint.os_version,
            'architecture': self.os_fingerprint.architecture,
            'processor_name': self.os_fingerprint.processor_name,
            'processor_count': self.os_fingerprint.processor_count,
            'processor_freq_mhz': self.os_fingerprint.processor_freq,
            'total_memory_gb': self.os_fingerprint.total_memory / (1024**3),
            'network_adapters': self.os_fingerprint.network_adapters,
            'disk_info': self.os_fingerprint.disk_info,
            'python_version': self.os_fingerprint.python_version,
            'hostname': self.os_fingerprint.hostname,
            'timestamp': self.os_fingerprint.timestamp
        }

    def get_system_hardware_info(self) -> Optional[Dict]:
        """Get system hardware information"""
        if not self.system_hardware:
            return None

        return {
            'cpu_model': self.system_hardware.cpu_model,
            'cpu_cores': self.system_hardware.cpu_cores,
            'cpu_threads': self.system_hardware.cpu_threads,
            'cpu_frequency_mhz': self.system_hardware.cpu_frequency_mhz,
            'ram_total_gb': self.system_hardware.ram_total_gb,
            'ram_available_gb': self.system_hardware.ram_available_gb,
            'network_interfaces': self.system_hardware.network_interfaces
        }

    def get_fingerprint_hash(self) -> str:
        """Generate a hash representing the entire system fingerprint"""
        if not self.os_fingerprint or not self.system_hardware:
            return ""

        fingerprint_data = {
            'os': self.os_fingerprint.os_name,
            'version': self.os_fingerprint.os_version,
            'arch': self.os_fingerprint.architecture,
            'cpu': self.system_hardware.cpu_model,
            'cores': self.system_hardware.cpu_cores,
            'ram': int(self.system_hardware.ram_total_gb),
            'interfaces': len(self.system_hardware.network_interfaces)
        }

        fingerprint_str = json.dumps(fingerprint_data, sort_keys=True)
        return hashlib.sha256(fingerprint_str.encode()).hexdigest()

    def spoof_fingerprint(self, target_config: Dict) -> None:
        """Spoof system fingerprint with target configuration"""
        if not self.os_fingerprint or not self.system_hardware:
            return

        # Update OS fingerprint
        if 'os_name' in target_config:
            self.os_fingerprint.os_name = target_config['os_name']
        if 'os_version' in target_config:
            self.os_fingerprint.os_version = target_config['os_version']
        if 'processor_name' in target_config:
            self.os_fingerprint.processor_name = target_config['processor_name']
        if 'processor_count' in target_config:
            self.os_fingerprint.processor_count = target_config['processor_count']
        if 'total_memory' in target_config:
            self.os_fingerprint.total_memory = target_config['total_memory']

        # Update hardware info
        if 'cpu_model' in target_config:
            self.system_hardware.cpu_model = target_config['cpu_model']
        if 'cpu_cores' in target_config:
            self.system_hardware.cpu_cores = target_config['cpu_cores']
        if 'cpu_threads' in target_config:
            self.system_hardware.cpu_threads = target_config['cpu_threads']
        if 'ram_total_gb' in target_config:
            self.system_hardware.ram_total_gb = target_config['ram_total_gb']

    def export_fingerprint_report(self, output_file: str = None) -> Dict:
        """Export comprehensive fingerprint report"""
        report = {
            'os_fingerprint': self.get_os_fingerprint(),
            'hardware_info': self.get_system_hardware_info(),
            'fingerprint_hash': self.get_fingerprint_hash(),
            'available_fingerprints': self.get_available_fingerprints(),
            'configured_proxies': self.get_configured_proxies()
        }

        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)

        return report


if __name__ == "__main__":
    # Test fingerprint manager with enhanced OS fingerprinting
    mgr = FingerprintManager()

    print("=" * 70)
    print("SYSTEM FINGERPRINT ANALYSIS")
    print("=" * 70)

    # Display OS Fingerprint
    os_fp = mgr.get_os_fingerprint()
    if os_fp:
        print("\nOperating System Information:")
        print(f"  OS: {os_fp['os_name']} {os_fp['os_version']}")
        print(f"  Architecture: {os_fp['architecture']}")
        print(f"  Hostname: {os_fp['hostname']}")
        print(f"  Python Version: {os_fp['python_version']}")

    # Display Hardware Info
    hw_info = mgr.get_system_hardware_info()
    if hw_info:
        print("\nHardware Information:")
        print(f"  CPU Model: {hw_info['cpu_model']}")
        print(f"  CPU Cores: {hw_info['cpu_cores']} (Threads: {hw_info['cpu_threads']})")
        print(f"  CPU Frequency: {hw_info['cpu_frequency_mhz']:.2f} MHz")
        print(f"  Total RAM: {hw_info['ram_total_gb']:.2f} GB")
        print(f"  Available RAM: {hw_info['ram_available_gb']:.2f} GB")

    # Display Network Adapters
    if hw_info and hw_info['network_interfaces']:
        print("\nNetwork Adapters:")
        for adapter in hw_info['network_interfaces']:
            print(f"  - {adapter['name']} ({adapter['status']})")
            if adapter['addresses']:
                for addr in adapter['addresses']:
                    print(f"    IP: {addr['address']}")
            if adapter['speed_mbps'] > 0:
                print(f"    Speed: {adapter['speed_mbps']} Mbps")

    # Display Disk Information
    if os_fp and os_fp['disk_info']:
        print("\nDisk Information:")
        for device, info in os_fp['disk_info'].items():
            print(f"  {device} ({info['fstype']})")
            print(f"    Total: {info['total_gb']:.2f} GB")
            print(f"    Used: {info['used_gb']:.2f} GB ({info['percent_used']:.1f}%)")
            print(f"    Free: {info['free_gb']:.2f} GB")

    # Display Fingerprint Hash
    fp_hash = mgr.get_fingerprint_hash()
    print(f"\nFingerprint Hash: {fp_hash}")

    print("\n" + "=" * 70)
    print("AVAILABLE FINGERPRINT PROFILES")
    print("=" * 70)
    print("\nAvailable Fingerprints:")
    for fp in mgr.get_available_fingerprints():
        print(f"  - {fp['name']} ({fp['id']})")

    print("\nAdding proxy...")
    proxy_id = mgr.add_proxy("http://proxy.example.com:8080", "http")
    print(f"Added proxy: {proxy_id}")

    print("\nConfigured Proxies:")
    for px in mgr.get_configured_proxies():
        print(f"  - {px['url']} ({px['type']})")

    # Export full report
    print("\n" + "=" * 70)
    print("EXPORTING FINGERPRINT REPORT")
    print("=" * 70)
    report_file = '/tmp/sc-fingerprints/fingerprint_report.json'
    mgr.export_fingerprint_report(report_file)
    print(f"Report exported to: {report_file}")
