"""
Credential Harvester Utility Functions
Provides supporting functions for credential harvesting operations
"""

import os
import json
import hashlib
import hmac
import base64
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import subprocess
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CredentialEntry:
    """Data class for storing credential information"""
    source: str
    url_or_host: str
    username: str
    password: str
    timestamp: str
    is_encrypted: bool = True
    metadata: Dict = None

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'source': self.source,
            'url_or_host': self.url_or_host,
            'username': self.username,
            'password': self.password,
            'timestamp': self.timestamp,
            'is_encrypted': self.is_encrypted,
            'metadata': self.metadata or {}
        }


class CredentialFilter:
    """Filters and analyzes harvested credentials"""

    @staticmethod
    def filter_by_source(credentials: List[CredentialEntry], source: str) -> List[CredentialEntry]:
        """Filter credentials by source"""
        return [c for c in credentials if c.source.lower() == source.lower()]

    @staticmethod
    def filter_by_username(credentials: List[CredentialEntry], username: str) -> List[CredentialEntry]:
        """Filter credentials by username"""
        return [c for c in credentials if c.username.lower() == username.lower()]

    @staticmethod
    def filter_by_url(credentials: List[CredentialEntry], url: str) -> List[CredentialEntry]:
        """Filter credentials by URL pattern"""
        return [c for c in credentials if url.lower() in c.url_or_host.lower()]

    @staticmethod
    def get_unique_hosts(credentials: List[CredentialEntry]) -> List[str]:
        """Extract unique hosts from credentials"""
        return list(set(c.url_or_host for c in credentials))

    @staticmethod
    def get_unique_usernames(credentials: List[CredentialEntry]) -> List[str]:
        """Extract unique usernames from credentials"""
        return list(set(c.username for c in credentials))

    @staticmethod
    def analyze_password_strength(password: str) -> Dict[str, any]:
        """Analyze password strength"""
        return {
            'length': len(password),
            'has_uppercase': any(c.isupper() for c in password),
            'has_lowercase': any(c.islower() for c in password),
            'has_digits': any(c.isdigit() for c in password),
            'has_special': any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password),
            'entropy': CredentialFilter._calculate_entropy(password)
        }

    @staticmethod
    def _calculate_entropy(password: str) -> float:
        """Calculate password entropy (bits)"""
        import math
        charset_size = 0
        if any(c.islower() for c in password):
            charset_size += 26
        if any(c.isupper() for c in password):
            charset_size += 26
        if any(c.isdigit() for c in password):
            charset_size += 10
        if any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            charset_size += 32

        if charset_size == 0:
            return 0
        return len(password) * math.log2(charset_size)


class CredentialVault:
    """Secure storage and management of harvested credentials"""

    def __init__(self, vault_path: str = None):
        """Initialize credential vault"""
        if vault_path is None:
            vault_path = str(Path.home() / '.credential_vault')

        self.vault_path = Path(vault_path)
        self.vault_path.mkdir(parents=True, exist_ok=True)
        self.credentials: List[CredentialEntry] = []
        self.salt = self._get_or_create_salt()

    def _get_or_create_salt(self) -> bytes:
        """Get or create a salt for credential operations"""
        salt_file = self.vault_path / '.salt'
        if salt_file.exists():
            with open(salt_file, 'rb') as f:
                return f.read()
        else:
            salt = os.urandom(32)
            with open(salt_file, 'wb') as f:
                f.write(salt)
            return salt

    def add_credential(self, credential: CredentialEntry) -> bool:
        """Add credential to vault"""
        try:
            self.credentials.append(credential)
            return True
        except Exception as e:
            print(f"[!] Error adding credential: {e}")
            return False

    def save_vault(self, password: str = None) -> bool:
        """Save vault to disk"""
        try:
            vault_data = {
                'timestamp': datetime.now().isoformat(),
                'credential_count': len(self.credentials),
                'credentials': [c.to_dict() for c in self.credentials]
            }

            vault_file = self.vault_path / 'vault.json'
            with open(vault_file, 'w') as f:
                json.dump(vault_data, f, indent=2)

            print(f"[+] Vault saved with {len(self.credentials)} credentials")
            return True
        except Exception as e:
            print(f"[!] Error saving vault: {e}")
            return False

    def load_vault(self, password: str = None) -> bool:
        """Load vault from disk"""
        try:
            vault_file = self.vault_path / 'vault.json'
            if not vault_file.exists():
                print("[-] Vault file not found")
                return False

            with open(vault_file, 'r') as f:
                vault_data = json.load(f)

            self.credentials = [
                CredentialEntry(
                    source=c['source'],
                    url_or_host=c['url_or_host'],
                    username=c['username'],
                    password=c['password'],
                    timestamp=c['timestamp'],
                    is_encrypted=c.get('is_encrypted', True),
                    metadata=c.get('metadata', {})
                )
                for c in vault_data.get('credentials', [])
            ]

            print(f"[+] Vault loaded with {len(self.credentials)} credentials")
            return True
        except Exception as e:
            print(f"[!] Error loading vault: {e}")
            return False

    def search_credentials(self, query: str, search_field: str = 'username') -> List[CredentialEntry]:
        """Search credentials by field"""
        results = []
        query_lower = query.lower()

        for cred in self.credentials:
            if search_field == 'username' and query_lower in cred.username.lower():
                results.append(cred)
            elif search_field == 'url' and query_lower in cred.url_or_host.lower():
                results.append(cred)
            elif search_field == 'source' and query_lower in cred.source.lower():
                results.append(cred)

        return results


class CredentialExporter:
    """Export credentials in various formats for analysis and exfiltration"""

    @staticmethod
    def export_json(credentials: List[CredentialEntry], filepath: str = None) -> str:
        """Export credentials as JSON"""
        data = {
            'exported': datetime.now().isoformat(),
            'count': len(credentials),
            'credentials': [c.to_dict() for c in credentials]
        }

        json_str = json.dumps(data, indent=2)

        if filepath:
            with open(filepath, 'w') as f:
                f.write(json_str)
            print(f"[+] Exported {len(credentials)} credentials to {filepath}")

        return json_str

    @staticmethod
    def export_csv(credentials: List[CredentialEntry], filepath: str = None) -> str:
        """Export credentials as CSV"""
        import csv
        from io import StringIO

        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['Source', 'URL/Host', 'Username', 'Password', 'Timestamp', 'Encrypted'])

        for cred in credentials:
            writer.writerow([
                cred.source,
                cred.url_or_host,
                cred.username,
                cred.password,
                cred.timestamp,
                cred.is_encrypted
            ])

        csv_str = output.getvalue()

        if filepath:
            with open(filepath, 'w') as f:
                f.write(csv_str)
            print(f"[+] Exported {len(credentials)} credentials to {filepath}")

        return csv_str

    @staticmethod
    def export_html(credentials: List[CredentialEntry], filepath: str = None) -> str:
        """Export credentials as HTML report"""
        html = """
        <html>
        <head>
            <title>Credential Harvest Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #4CAF50; color: white; }
                tr:nth-child(even) { background-color: #f2f2f2; }
                .summary { margin-bottom: 20px; }
            </style>
        </head>
        <body>
            <h1>Credential Harvest Report</h1>
            <div class="summary">
                <p><strong>Generated:</strong> {timestamp}</p>
                <p><strong>Total Credentials:</strong> {count}</p>
            </div>
            <table>
                <tr>
                    <th>Source</th>
                    <th>URL/Host</th>
                    <th>Username</th>
                    <th>Password</th>
                    <th>Timestamp</th>
                </tr>
                {rows}
            </table>
        </body>
        </html>
        """

        rows = ""
        for cred in credentials:
            rows += f"""
            <tr>
                <td>{cred.source}</td>
                <td>{cred.url_or_host}</td>
                <td>{cred.username}</td>
                <td>{"*" * len(cred.password) if cred.password else ""}</td>
                <td>{cred.timestamp}</td>
            </tr>
            """

        html = html.format(
            timestamp=datetime.now().isoformat(),
            count=len(credentials),
            rows=rows
        )

        if filepath:
            with open(filepath, 'w') as f:
                f.write(html)
            print(f"[+] Exported {len(credentials)} credentials to {filepath}")

        return html

    @staticmethod
    def export_text(credentials: List[CredentialEntry], filepath: str = None) -> str:
        """Export credentials as formatted text"""
        lines = []
        lines.append("=" * 100)
        lines.append("CREDENTIAL HARVEST REPORT")
        lines.append(f"Generated: {datetime.now().isoformat()}")
        lines.append(f"Total Credentials: {len(credentials)}")
        lines.append("=" * 100)

        for i, cred in enumerate(credentials, 1):
            lines.append(f"\n[{i}] {cred.source.upper()}")
            lines.append(f"    URL/Host: {cred.url_or_host}")
            lines.append(f"    Username: {cred.username}")
            lines.append(f"    Password: {cred.password}")
            lines.append(f"    Timestamp: {cred.timestamp}")

        lines.append("\n" + "=" * 100)

        text = '\n'.join(lines)

        if filepath:
            with open(filepath, 'w') as f:
                f.write(text)
            print(f"[+] Exported {len(credentials)} credentials to {filepath}")

        return text


class CredentialAnalyzer:
    """Analyze harvested credentials for patterns and vulnerabilities"""

    @staticmethod
    def find_duplicate_passwords(credentials: List[CredentialEntry]) -> Dict[str, List[str]]:
        """Find passwords used multiple times"""
        password_map = {}
        for cred in credentials:
            if cred.password not in password_map:
                password_map[cred.password] = []
            password_map[cred.password].append(f"{cred.username}@{cred.url_or_host}")

        duplicates = {pwd: hosts for pwd, hosts in password_map.items() if len(hosts) > 1}
        return duplicates

    @staticmethod
    def find_weak_passwords(credentials: List[CredentialEntry]) -> List[CredentialEntry]:
        """Find weak passwords"""
        weak = []
        for cred in credentials:
            strength = CredentialFilter.analyze_password_strength(cred.password)
            # Consider weak if entropy < 50 bits
            if strength['entropy'] < 50:
                weak.append(cred)
        return weak

    @staticmethod
    def find_password_patterns(credentials: List[CredentialEntry]) -> Dict[str, List[str]]:
        """Find common password patterns"""
        patterns = {}

        for cred in credentials:
            pwd = cred.password

            # Check for common patterns
            if pwd and len(pwd) <= 6:
                pattern_type = 'very_short'
            elif pwd == cred.username:
                pattern_type = 'username_as_password'
            elif pwd.lower() == cred.url_or_host.split('.')[0].lower():
                pattern_type = 'domain_as_password'
            elif all(c.isdigit() for c in pwd):
                pattern_type = 'only_numbers'
            elif pwd in ['password', '123456', 'admin', 'letmein', 'welcome', '']:
                pattern_type = 'common_password'
            else:
                continue

            if pattern_type not in patterns:
                patterns[pattern_type] = []
            patterns[pattern_type].append(f"{cred.username}@{cred.url_or_host}")

        return patterns

    @staticmethod
    def generate_report(credentials: List[CredentialEntry]) -> str:
        """Generate comprehensive analysis report"""
        report = []
        report.append("\n" + "=" * 80)
        report.append("CREDENTIAL ANALYSIS REPORT")
        report.append("=" * 80)

        # Summary
        report.append(f"\nTotal Credentials Harvested: {len(credentials)}")
        sources = set(c.source for c in credentials)
        report.append(f"Sources: {', '.join(sources)}")

        # Duplicates
        duplicates = CredentialAnalyzer.find_duplicate_passwords(credentials)
        if duplicates:
            report.append(f"\n[!] Found {len(duplicates)} passwords used multiple times:")
            for pwd, hosts in duplicates.items():
                report.append(f"    Password used on {len(hosts)} accounts:")
                for host in hosts[:5]:  # Show first 5
                    report.append(f"      - {host}")

        # Weak passwords
        weak = CredentialAnalyzer.find_weak_passwords(credentials)
        if weak:
            report.append(f"\n[!] Found {len(weak)} weak passwords:")
            for cred in weak[:10]:  # Show first 10
                report.append(f"    {cred.username}@{cred.url_or_host}")

        # Patterns
        patterns = CredentialAnalyzer.find_password_patterns(credentials)
        if patterns:
            report.append(f"\n[!] Found dangerous password patterns:")
            for pattern, accounts in patterns.items():
                report.append(f"    {pattern}: {len(accounts)} accounts")

        report.append("\n" + "=" * 80)
        return '\n'.join(report)


def main():
    """Demonstration of utility functions"""
    print("[*] Credential Harvester Utilities")
    print("[*] ==================================\n")

    # Create sample credentials
    credentials = [
        CredentialEntry(
            source='chrome',
            url_or_host='example.com',
            username='admin',
            password='password123',
            timestamp=datetime.now().isoformat()
        ),
        CredentialEntry(
            source='windows_credential_manager',
            url_or_host='server.local',
            username='user@domain.com',
            password='MyP@ssw0rd!',
            timestamp=datetime.now().isoformat()
        ),
        CredentialEntry(
            source='rdp',
            url_or_host='192.168.1.100',
            username='administrator',
            password='123456',
            timestamp=datetime.now().isoformat()
        ),
    ]

    # Export in various formats
    print("[*] Exporting credentials...")
    CredentialExporter.export_json(credentials, '/tmp/creds.json')
    CredentialExporter.export_csv(credentials, '/tmp/creds.csv')
    CredentialExporter.export_html(credentials, '/tmp/creds.html')

    # Analyze credentials
    print("\n[*] Analyzing credentials...")
    print(CredentialAnalyzer.generate_report(credentials))


if __name__ == '__main__':
    main()
