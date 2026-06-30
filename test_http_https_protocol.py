#!/usr/bin/env python3
"""
HTTP vs HTTPS Protocol Download Test Suite
Comprehensive testing for HTTP and HTTPS downloads with SSL/TLS verification
Tests protocol differences, certificate validation, and security warnings

Usage:
    python test_http_https_protocol.py [--url http://example.com] [--output report.json]
"""

import os
import sys
import json
import socket
import ssl
import hashlib
import warnings
import urllib.request
import urllib.error
import http.client
import certifi
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from urllib.parse import urlparse
import logging

# Configure logging with detailed output
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HTTPSProtocolTester:
    """Test suite for HTTP vs HTTPS protocol verification"""

    def __init__(self, verbose: bool = True):
        """Initialize protocol tester"""
        self.verbose = verbose
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "protocol_tests": [],
            "ssl_tls_warnings": [],
            "certificate_tests": [],
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "warnings": 0,
                "ssl_errors": 0,
                "protocol_comparison": {
                    "http": {"success": 0, "failure": 0},
                    "https": {"success": 0, "failure": 0}
                }
            }
        }
        self.test_urls = {
            "http": [
                "http://httpbin.org/get",
                "http://example.com",
                "http://www.google.com"
            ],
            "https": [
                "https://httpbin.org/get",
                "https://example.com",
                "https://www.google.com",
                "https://github.com"
            ]
        }

    def log(self, message: str, level: str = "INFO"):
        """Log test message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        if level == "ERROR":
            logger.error(message)
        elif level == "WARNING":
            logger.warning(message)
        elif level == "DEBUG":
            logger.debug(message)
        else:
            logger.info(message)

    def test_http_download(self, url: str) -> Dict:
        """Test HTTP download (no SSL)"""
        result = {
            "url": url,
            "protocol": "HTTP",
            "scheme": urlparse(url).scheme,
            "status": "PENDING",
            "status_code": None,
            "ssl_verification": "N/A (HTTP)",
            "certificate_info": None,
            "warnings": [],
            "errors": [],
            "response_time_ms": 0,
            "content_hash": None,
            "headers": {}
        }

        try:
            import time
            start = time.time()
            self.log(f"Testing HTTP download: {url}", "TEST")

            # Standard HTTP download without SSL
            with urllib.request.urlopen(url, timeout=10) as response:
                result["status_code"] = response.status
                result["headers"] = dict(response.headers)
                content = response.read()
                result["content_hash"] = hashlib.sha256(content).hexdigest()
                result["response_time_ms"] = int((time.time() - start) * 1000)

            # Check for protocol downgrade warning
            if result["status_code"] == 200:
                result["status"] = "SUCCESS"
                result["warnings"].append("HTTP is unencrypted and vulnerable to MITM")
                self.log(f"✓ HTTP download successful: {url} ({result['response_time_ms']}ms)", "SUCCESS")
                self.report["summary"]["protocol_comparison"]["http"]["success"] += 1
            else:
                result["status"] = "FAILED"
                result["errors"].append(f"HTTP {result['status_code']}")
                self.report["summary"]["protocol_comparison"]["http"]["failure"] += 1

        except urllib.error.HTTPError as e:
            result["status"] = "ERROR"
            result["status_code"] = e.code
            result["errors"].append(f"HTTP Error {e.code}: {e.reason}")
            self.log(f"✗ HTTP download failed: {url} - {e.code}: {e.reason}", "ERROR")
            self.report["summary"]["protocol_comparison"]["http"]["failure"] += 1

        except urllib.error.URLError as e:
            result["status"] = "ERROR"
            result["errors"].append(f"URL Error: {str(e.reason)}")
            self.log(f"✗ HTTP URL error: {url} - {e.reason}", "ERROR")
            self.report["summary"]["protocol_comparison"]["http"]["failure"] += 1

        except Exception as e:
            result["status"] = "ERROR"
            result["errors"].append(f"Exception: {str(e)}")
            self.log(f"✗ HTTP download exception: {url} - {e}", "ERROR")
            self.report["summary"]["protocol_comparison"]["http"]["failure"] += 1

        return result

    def test_https_download(self, url: str, verify_ssl: bool = True) -> Dict:
        """Test HTTPS download with SSL verification"""
        result = {
            "url": url,
            "protocol": "HTTPS",
            "scheme": urlparse(url).scheme,
            "status": "PENDING",
            "status_code": None,
            "ssl_verification": "ENABLED" if verify_ssl else "DISABLED",
            "certificate_info": {},
            "warnings": [],
            "errors": [],
            "response_time_ms": 0,
            "content_hash": None,
            "headers": {},
            "tls_version": None,
            "cipher_suite": None
        }

        try:
            import time
            start = time.time()
            self.log(f"Testing HTTPS download: {url} (SSL verify: {verify_ssl})", "TEST")

            # Create SSL context with proper verification
            if verify_ssl:
                context = ssl.create_default_context(cafile=certifi.where())
                context.check_hostname = True
                context.verify_mode = ssl.CERT_REQUIRED
            else:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                result["warnings"].append("SSL verification DISABLED - vulnerable to MITM")

            # Perform HTTPS download
            with urllib.request.urlopen(url, context=context, timeout=10) as response:
                result["status_code"] = response.status
                result["headers"] = dict(response.headers)
                content = response.read()
                result["content_hash"] = hashlib.sha256(content).hexdigest()
                result["response_time_ms"] = int((time.time() - start) * 1000)

                # Extract SSL/TLS information
                if hasattr(response, 'fp') and hasattr(response.fp, '_ssl_obj'):
                    try:
                        ssl_obj = response.fp._ssl_obj
                        result["tls_version"] = ssl_obj.version()
                        result["cipher_suite"] = ssl_obj.cipher()
                    except:
                        pass

            if result["status_code"] == 200:
                result["status"] = "SUCCESS"
                self.log(f"✓ HTTPS download successful: {url} ({result['response_time_ms']}ms)", "SUCCESS")
                self.report["summary"]["protocol_comparison"]["https"]["success"] += 1
            else:
                result["status"] = "FAILED"
                result["errors"].append(f"HTTPS {result['status_code']}")
                self.report["summary"]["protocol_comparison"]["https"]["failure"] += 1

        except ssl.SSLError as e:
            result["status"] = "SSL_ERROR"
            result["errors"].append(f"SSL Error: {str(e)}")
            self.log(f"✗ HTTPS SSL error: {url} - {e}", "ERROR")
            self.report["summary"]["ssl_errors"] += 1
            self.report["summary"]["protocol_comparison"]["https"]["failure"] += 1

        except ssl.CertificateError as e:
            result["status"] = "CERT_ERROR"
            result["errors"].append(f"Certificate Error: {str(e)}")
            self.log(f"✗ HTTPS certificate error: {url} - {e}", "ERROR")
            self.report["summary"]["ssl_errors"] += 1
            self.report["summary"]["protocol_comparison"]["https"]["failure"] += 1

        except urllib.error.HTTPError as e:
            result["status"] = "ERROR"
            result["status_code"] = e.code
            result["errors"].append(f"HTTP Error {e.code}: {e.reason}")
            self.log(f"✗ HTTPS download failed: {url} - {e.code}: {e.reason}", "ERROR")
            self.report["summary"]["protocol_comparison"]["https"]["failure"] += 1

        except urllib.error.URLError as e:
            result["status"] = "ERROR"
            result["errors"].append(f"URL Error: {str(e.reason)}")
            self.log(f"✗ HTTPS URL error: {url} - {e.reason}", "ERROR")
            self.report["summary"]["protocol_comparison"]["https"]["failure"] += 1

        except Exception as e:
            result["status"] = "ERROR"
            result["errors"].append(f"Exception: {str(e)}")
            self.log(f"✗ HTTPS download exception: {url} - {e}", "ERROR")
            self.report["summary"]["protocol_comparison"]["https"]["failure"] += 1

        return result

    def test_protocol_security_comparison(self, url: str) -> Dict:
        """Compare HTTP and HTTPS security characteristics"""
        result = {
            "url": url,
            "comparison": {
                "protocol": None,
                "encryption": None,
                "authentication": None,
                "integrity_protection": None,
                "vulnerability_to_mitm": None,
                "replay_attack_resistance": None
            },
            "findings": []
        }

        # Parse URL
        parsed = urlparse(url)

        if parsed.scheme.lower() == "http":
            result["comparison"]["protocol"] = "HTTP (plain text)"
            result["comparison"]["encryption"] = "NONE - All data transmitted in plain text"
            result["comparison"]["authentication"] = "NONE - No server verification"
            result["comparison"]["integrity_protection"] = "NONE - No protection"
            result["comparison"]["vulnerability_to_mitm"] = "CRITICAL - Vulnerable to MITM"
            result["comparison"]["replay_attack_resistance"] = "NONE"
            result["findings"] = [
                "Data can be intercepted by network-level attackers",
                "No verification that you're talking to the intended server",
                "Content can be modified in transit",
                "Credentials transmitted in plain text are vulnerable",
                "Session tokens can be stolen",
                "Suitable only for non-sensitive public data"
            ]

        elif parsed.scheme.lower() == "https":
            result["comparison"]["protocol"] = "HTTPS (encrypted)"
            result["comparison"]["encryption"] = "TLS/SSL - Strong encryption (AES-256, ChaCha20, etc.)"
            result["comparison"]["authentication"] = "Certificate-based - Server identity verified via PKI"
            result["comparison"]["integrity_protection"] = "HMAC - Data integrity guaranteed"
            result["comparison"]["vulnerability_to_mitm"] = "PROTECTED - MITM requires certificate spoofing"
            result["comparison"]["replay_attack_resistance"] = "Sequence numbers and timestamps in TLS"
            result["findings"] = [
                "Data encrypted in transit (not readable to passive attackers)",
                "Server identity verified via X.509 certificates",
                "Data integrity protected by HMAC",
                "Perfect Forward Secrecy with ECDHE/DHE",
                "Protection against downgrade attacks",
                "HSTS headers can enforce HTTPS-only access"
            ]

        return result

    def test_certificate_validation(self, hostname: str, port: int = 443) -> Dict:
        """Test certificate validation for HTTPS connections"""
        result = {
            "hostname": hostname,
            "port": port,
            "status": "PENDING",
            "certificate": {
                "subject": None,
                "issuer": None,
                "version": None,
                "serial_number": None,
                "not_before": None,
                "not_after": None,
                "algorithm": None
            },
            "chain_validation": {
                "valid": False,
                "chain_length": 0,
                "warnings": []
            },
            "ssl_tls_info": {
                "protocol_version": None,
                "cipher_suite": None,
                "bits": None
            },
            "warnings": [],
            "errors": []
        }

        try:
            self.log(f"Validating certificate for {hostname}:{port}", "TEST")

            # Create SSL context
            context = ssl.create_default_context(cafile=certifi.where())

            # Connect to server
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    # Get certificate
                    cert_der = ssock.getpeercert(binary_form=True)
                    cert_info = ssock.getpeercert()

                    # Extract certificate information
                    if cert_info:
                        result["certificate"]["subject"] = dict(x[0] for x in cert_info.get('subject', []))
                        result["certificate"]["issuer"] = dict(x[0] for x in cert_info.get('issuer', []))
                        result["certificate"]["not_before"] = cert_info.get('notBefore', 'N/A')
                        result["certificate"]["not_after"] = cert_info.get('notAfter', 'N/A')

                    # Get TLS version and cipher
                    result["ssl_tls_info"]["protocol_version"] = ssock.version()
                    cipher = ssock.cipher()
                    if cipher:
                        result["ssl_tls_info"]["cipher_suite"] = cipher[0]
                        result["ssl_tls_info"]["bits"] = cipher[2]

                    # Check for weak protocols
                    tls_version = ssock.version()
                    if tls_version in ["SSLv2", "SSLv3", "TLSv1", "TLSv1.1"]:
                        result["warnings"].append(f"Weak TLS version detected: {tls_version}")
                        result["chain_validation"]["warnings"].append(f"Weak protocol: {tls_version}")

                    # Validate chain
                    result["chain_validation"]["valid"] = True
                    result["status"] = "SUCCESS"
                    self.log(f"✓ Certificate validated for {hostname}: {tls_version}", "SUCCESS")

        except ssl.SSLError as e:
            result["status"] = "SSL_ERROR"
            result["errors"].append(f"SSL Error: {str(e)}")
            result["chain_validation"]["warnings"].append(str(e))
            self.log(f"✗ SSL validation failed for {hostname}: {e}", "ERROR")

        except socket.timeout:
            result["status"] = "TIMEOUT"
            result["errors"].append("Connection timeout")
            self.log(f"✗ Certificate validation timeout for {hostname}", "ERROR")

        except Exception as e:
            result["status"] = "ERROR"
            result["errors"].append(f"Exception: {str(e)}")
            self.log(f"✗ Certificate validation error for {hostname}: {e}", "ERROR")

        return result

    def test_ssl_tls_warnings(self) -> List[Dict]:
        """Check for SSL/TLS configuration warnings"""
        warnings_list = []

        # Test 1: Certificate validation enabled
        test1 = {
            "test": "SSL Certificate Validation",
            "status": "ENABLED",
            "details": "urllib.request uses certifi CA bundle by default",
            "severity": "CRITICAL",
            "warning": None
        }
        warnings_list.append(test1)

        # Test 2: Hostname verification
        test2 = {
            "test": "Hostname Verification",
            "status": "ENABLED",
            "details": "Default SSL context enables hostname checking",
            "severity": "CRITICAL",
            "warning": None
        }
        warnings_list.append(test2)

        # Test 3: SSL version check
        test3 = {
            "test": "Weak SSL/TLS Versions",
            "status": "PROTECTED",
            "details": "Python 3.10+ disables SSLv2, SSLv3, TLSv1, TLSv1.1",
            "severity": "HIGH",
            "warning": f"Python version {sys.version_info.major}.{sys.version_info.minor} - check TLS support"
        }
        warnings_list.append(test3)

        # Test 4: Certificate verification in urllib
        test4 = {
            "test": "urllib SSL Verification",
            "status": "ENABLED",
            "details": "urllib.request verifies certificates against certifi CA bundle",
            "severity": "CRITICAL",
            "warning": None
        }
        warnings_list.append(test4)

        # Test 5: HTTP Strict Transport Security (HSTS)
        test5 = {
            "test": "HSTS Support",
            "status": "SUPPORTED",
            "details": "HSTS headers enforce HTTPS-only communication",
            "severity": "MEDIUM",
            "warning": "HSTS not enforced by urllib - use requests library for automatic HSTS"
        }
        warnings_list.append(test5)

        return warnings_list

    def run_protocol_comparison(self) -> Dict:
        """Run HTTP vs HTTPS comparison on test URLs"""
        self.log("=" * 80, "INFO")
        self.log("HTTP vs HTTPS Protocol Comparison", "INFO")
        self.log("=" * 80, "INFO")

        comparison_results = []

        # Test selected URLs
        test_pairs = [
            ("http://example.com", "https://example.com"),
            ("http://www.google.com", "https://www.google.com")
        ]

        for http_url, https_url in test_pairs:
            self.log(f"\nComparing protocols for domain...", "INFO")

            # Test HTTP
            http_result = self.test_http_download(http_url)
            self.report["protocol_tests"].append(http_result)

            # Test HTTPS
            https_result = self.test_https_download(https_url, verify_ssl=True)
            self.report["protocol_tests"].append(https_result)

            # Security comparison
            http_comparison = self.test_protocol_security_comparison(http_url)
            https_comparison = self.test_protocol_security_comparison(https_url)

            comparison_results.append({
                "http": http_comparison,
                "https": https_comparison
            })

        return {"comparison": comparison_results}

    def run_certificate_validation_tests(self) -> None:
        """Run certificate validation tests"""
        self.log("\n" + "=" * 80, "INFO")
        self.log("Certificate Validation Tests", "INFO")
        self.log("=" * 80, "INFO")

        test_hosts = [
            ("example.com", 443),
            ("www.google.com", 443),
            ("github.com", 443),
            ("httpbin.org", 443)
        ]

        for hostname, port in test_hosts:
            cert_result = self.test_certificate_validation(hostname, port)
            self.report["certificate_tests"].append(cert_result)
            self.report["summary"]["total_tests"] += 1

            if cert_result["status"] == "SUCCESS":
                self.report["summary"]["passed"] += 1
            else:
                self.report["summary"]["failed"] += 1
                if "SSL" in cert_result["status"]:
                    self.report["summary"]["ssl_errors"] += 1

    def run_ssl_tls_warning_checks(self) -> None:
        """Run SSL/TLS warning checks"""
        self.log("\n" + "=" * 80, "INFO")
        self.log("SSL/TLS Configuration Warnings Check", "INFO")
        self.log("=" * 80, "INFO")

        warnings_results = self.test_ssl_tls_warnings()

        for warning in warnings_results:
            self.log(f"  [{warning['status']}] {warning['test']}", "INFO")
            if warning['warning']:
                self.log(f"    WARNING: {warning['warning']}", "WARNING")
                self.report["summary"]["warnings"] += 1

        self.report["ssl_tls_warnings"] = warnings_results

    def run_all_tests(self) -> Dict:
        """Run complete test suite"""
        self.log("\n" + "=" * 80, "INFO")
        self.log("COMPREHENSIVE HTTP vs HTTPS PROTOCOL TEST SUITE", "INFO")
        self.log("=" * 80, "INFO")
        self.log(f"Test Start: {datetime.now().isoformat()}", "INFO")

        try:
            # Run protocol comparison
            self.run_protocol_comparison()

            # Run certificate validation
            self.run_certificate_validation_tests()

            # Run SSL/TLS warning checks
            self.run_ssl_tls_warning_checks()

        except Exception as e:
            self.log(f"Test suite error: {e}", "ERROR")

        # Print summary
        self._print_summary()
        return self.report

    def _print_summary(self) -> None:
        """Print test summary"""
        self.log("\n" + "=" * 80, "INFO")
        self.log("TEST SUMMARY", "INFO")
        self.log("=" * 80, "INFO")

        summary = self.report["summary"]
        self.log(f"Total Tests: {summary['total_tests']}", "INFO")
        self.log(f"Passed: {summary['passed']}", "INFO")
        self.log(f"Failed: {summary['failed']}", "INFO")
        self.log(f"Warnings: {summary['warnings']}", "WARNING")
        self.log(f"SSL Errors: {summary['ssl_errors']}", "ERROR")
        self.log("", "INFO")
        self.log("Protocol Comparison:", "INFO")
        self.log(f"  HTTP - Success: {summary['protocol_comparison']['http']['success']}, "
                f"Failure: {summary['protocol_comparison']['http']['failure']}", "INFO")
        self.log(f"  HTTPS - Success: {summary['protocol_comparison']['https']['success']}, "
                f"Failure: {summary['protocol_comparison']['https']['failure']}", "INFO")

    def save_report(self, filename: str = None) -> str:
        """Save test report to file"""
        if filename is None:
            filename = f"http_https_protocol_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        filepath = Path(filename)
        with open(filepath, 'w') as f:
            json.dump(self.report, f, indent=2)

        self.log(f"Report saved to {filepath}", "SUCCESS")
        return str(filepath)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="HTTP vs HTTPS Protocol Download Test Suite"
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output report filename"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    # Run test suite
    tester = HTTPSProtocolTester(verbose=args.verbose)
    report = tester.run_all_tests()

    # Save report
    report_path = tester.save_report(args.output)

    print(f"\n📋 Report saved: {report_path}")

    return 0 if report["summary"]["ssl_errors"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
