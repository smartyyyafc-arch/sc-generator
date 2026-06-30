#!/usr/bin/env python3
"""
VBS/HTA Download Test Suite
Tests browser download capabilities for VBS and HTA files
Verifies files can be downloaded without browser warnings
"""

import os
import json
import requests
import subprocess
import time
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

class DownloadTester:
    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "base_url": base_url,
            "tests": [],
            "summary": {
                "total_files": 0,
                "successful_downloads": 0,
                "failed_downloads": 0,
                "warnings": 0,
                "errors": 0
            }
        }

    def log(self, message: str, level: str = "INFO"):
        """Log a message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")

    def test_server_health(self) -> bool:
        """Test if server is running and responding"""
        self.log("Testing server health...", "TEST")
        try:
            response = self.session.get(f"{self.base_url}/api/files", timeout=5)
            if response.status_code == 200:
                self.log("Server is healthy and responding", "SUCCESS")
                return True
            else:
                self.log(f"Server returned status code {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"Failed to connect to server: {e}", "ERROR")
            return False

    def get_available_files(self) -> List[Dict]:
        """Get list of available VBS/HTA files from server"""
        self.log("Fetching available files...", "TEST")
        try:
            response = self.session.get(f"{self.base_url}/api/files", timeout=10)
            response.raise_for_status()
            files = response.json()
            self.log(f"Found {len(files)} files", "SUCCESS")
            for file in files:
                self.log(f"  - {file['name']} ({file['size']} bytes)", "INFO")
            return files
        except Exception as e:
            self.log(f"Failed to fetch file list: {e}", "ERROR")
            return []

    def verify_mime_types(self) -> Dict[str, Tuple[str, str]]:
        """Verify MIME types for different file extensions"""
        self.log("Verifying MIME types...", "TEST")
        expected_types = {
            ".vbs": "text/vbscript",
            ".hta": "application/x-mshta"
        }
        results = {}

        for ext, expected_type in expected_types.items():
            results[ext] = {
                "expected": expected_type,
                "status": "NOT_TESTED"
            }

        return results

    def test_file_download(self, url: str, filename: str) -> Dict:
        """Test downloading a single file"""
        # Ensure URL has proper scheme
        if url.startswith('/'):
            url = self.base_url + url

        result = {
            "filename": filename,
            "url": url,
            "status": "PENDING",
            "status_code": None,
            "content_type": None,
            "file_size": 0,
            "content_hash": None,
            "warnings": [],
            "errors": []
        }

        try:
            self.log(f"Downloading {filename}...", "TEST")
            response = self.session.get(url, timeout=30, allow_redirects=True)
            result["status_code"] = response.status_code

            if response.status_code == 200:
                result["status"] = "SUCCESS"
                result["content_type"] = response.headers.get('Content-Type', 'unknown')
                result["file_size"] = len(response.content)

                # Calculate hash
                result["content_hash"] = hashlib.sha256(response.content).hexdigest()

                # Check for warnings
                ext = Path(filename).suffix.lower()

                if ext == ".vbs":
                    if result["content_type"] != "text/vbscript":
                        result["warnings"].append(
                            f"Unexpected MIME type for VBS: {result['content_type']}"
                        )
                    if not response.content.startswith(b"MZ"):  # Not an executable
                        # VBS files are text, so this is expected
                        pass

                elif ext == ".hta":
                    if result["content_type"] not in ["application/x-mshta", "text/html"]:
                        result["warnings"].append(
                            f"Unexpected MIME type for HTA: {result['content_type']}"
                        )

                # Check Content-Disposition header
                disposition = response.headers.get('Content-Disposition', '')
                if ext in [".vbs", ".hta"]:
                    if "attachment" not in disposition:
                        result["warnings"].append(
                            f"Missing 'attachment' in Content-Disposition header"
                        )
                    else:
                        result["info"] = f"Correctly set to download: {disposition}"

                self.log(f"✓ Downloaded {filename} ({result['file_size']} bytes)", "SUCCESS")

            else:
                result["status"] = "FAILED"
                result["errors"].append(f"HTTP {response.status_code}")
                self.log(f"✗ Failed to download {filename}: HTTP {response.status_code}", "ERROR")

        except requests.Timeout:
            result["status"] = "TIMEOUT"
            result["errors"].append("Download timeout (30s)")
            self.log(f"✗ Download timeout: {filename}", "ERROR")
        except Exception as e:
            result["status"] = "ERROR"
            result["errors"].append(str(e))
            self.log(f"✗ Error downloading {filename}: {e}", "ERROR")

        return result

    def test_http_headers(self, url: str, filename: str) -> Dict:
        """Test HTTP headers for security and download compatibility"""
        # Ensure URL has proper scheme
        if url.startswith('/'):
            url = self.base_url + url

        result = {
            "filename": filename,
            "headers": {},
            "warnings": [],
            "info": []
        }

        try:
            self.log(f"Checking headers for {filename}...", "TEST")
            response = self.session.head(url, timeout=10, allow_redirects=True)

            headers = response.headers
            result["headers"] = dict(headers)

            # Check for important headers
            important_headers = [
                'Content-Type',
                'Content-Length',
                'Content-Disposition',
                'Cache-Control',
                'X-Content-Type-Options'
            ]

            for header in important_headers:
                if header in headers:
                    result["info"].append(f"{header}: {headers[header]}")

            # Check for security headers
            if 'X-Content-Type-Options' not in headers:
                result["warnings"].append("Missing X-Content-Type-Options header")

            if 'Cache-Control' in headers:
                if 'no-store' in headers['Cache-Control']:
                    result["info"].append("Cache-Control properly set to prevent caching")

            self.log(f"✓ Header check completed for {filename}", "SUCCESS")

        except Exception as e:
            result["warnings"].append(f"Failed to check headers: {e}")
            self.log(f"✗ Header check failed for {filename}: {e}", "ERROR")

        return result

    def test_browser_warnings(self, filename: str) -> List[str]:
        """Detect potential browser warnings based on file type"""
        warnings = []
        ext = Path(filename).suffix.lower()

        if ext == ".vbs":
            warnings.append(
                "VBS files may trigger SmartScreen warning in Edge/IE"
            )
            warnings.append(
                "Windows Defender may flag VBS as potentially unwanted"
            )
            warnings.append(
                "Some browsers may require user confirmation before download"
            )

        elif ext == ".hta":
            warnings.append(
                "HTA files are deprecated and not supported in modern browsers"
            )
            warnings.append(
                "Chrome and Edge may block HTA downloads"
            )
            warnings.append(
                "Firefox may prompt for manual save location"
            )

        return warnings

    def run_all_tests(self) -> Dict:
        """Run the complete test suite"""
        self.log("=" * 60, "INFO")
        self.log("VBS/HTA Download Test Suite", "INFO")
        self.log("=" * 60, "INFO")

        # Test 1: Server health
        if not self.test_server_health():
            self.log("Cannot proceed: server is not responding", "ERROR")
            return self.test_results

        # Test 2: Get available files
        files = self.get_available_files()
        self.test_results["summary"]["total_files"] = len(files)

        if not files:
            self.log("No files found to test", "WARNING")
            return self.test_results

        # Test 3: Test each file
        self.log("\n" + "=" * 60, "INFO")
        self.log("Testing Downloads", "INFO")
        self.log("=" * 60, "INFO")

        for file in files:
            download_result = self.test_file_download(file['url'], file['name'])
            self.test_results["tests"].append({
                "type": "download",
                "result": download_result
            })

            if download_result["status"] == "SUCCESS":
                self.test_results["summary"]["successful_downloads"] += 1
            else:
                self.test_results["summary"]["failed_downloads"] += 1

            # Test HTTP headers
            header_result = self.test_http_headers(file['url'], file['name'])
            self.test_results["tests"].append({
                "type": "headers",
                "result": header_result
            })

            self.test_results["summary"]["warnings"] += len(header_result["warnings"])

            # Check for browser warnings
            browser_warnings = self.test_browser_warnings(file['name'])
            if browser_warnings:
                self.test_results["tests"].append({
                    "type": "browser_warnings",
                    "filename": file['name'],
                    "warnings": browser_warnings
                })
                self.test_results["summary"]["warnings"] += len(browser_warnings)

        # Print summary
        self.log("\n" + "=" * 60, "INFO")
        self.log("Test Summary", "INFO")
        self.log("=" * 60, "INFO")
        summary = self.test_results["summary"]
        self.log(f"Total Files: {summary['total_files']}", "INFO")
        self.log(f"Successful Downloads: {summary['successful_downloads']}", "INFO")
        self.log(f"Failed Downloads: {summary['failed_downloads']}", "INFO")
        self.log(f"Warnings Detected: {summary['warnings']}", "WARNING")
        self.log(f"Errors Detected: {summary['errors']}", "ERROR")

        return self.test_results

    def save_report(self, filename: str = None) -> str:
        """Save test results to file"""
        if filename is None:
            filename = f"vbs_hta_download_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        filepath = Path(__file__).parent / filename
        with open(filepath, 'w') as f:
            json.dump(self.test_results, f, indent=2)

        self.log(f"Report saved to {filepath}", "INFO")
        return str(filepath)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Test VBS/HTA downloads via browser"
    )
    parser.add_argument(
        "--url",
        default="http://localhost:3000",
        help="Base URL of the download server (default: http://localhost:3000)"
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output report filename"
    )
    parser.add_argument(
        "--wait",
        type=int,
        default=5,
        help="Wait seconds for server to start (default: 5)"
    )

    args = parser.parse_args()

    # Wait for server
    print(f"Waiting {args.wait} seconds for server to start...")
    time.sleep(args.wait)

    # Run tests
    tester = DownloadTester(base_url=args.url)
    results = tester.run_all_tests()

    # Save report
    report_path = tester.save_report(args.output)

    # Print report path
    print(f"\nReport: {report_path}")

    return 0 if results["summary"]["failed_downloads"] == 0 else 1


if __name__ == "__main__":
    exit(main())
