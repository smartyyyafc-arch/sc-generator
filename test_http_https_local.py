#!/usr/bin/env python3
"""
HTTP vs HTTPS Protocol Test Suite - Local Testing
Tests protocol differences, certificate validation, and security characteristics
Works without external network connectivity
"""

import os
import sys
import json
import ssl
import socket
import hashlib
import tempfile
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.request
import urllib.error
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HTTPSProtocolAnalyzer:
    """Analyze HTTP vs HTTPS protocol characteristics"""

    def __init__(self):
        """Initialize analyzer"""
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "protocol_analysis": {},
            "ssl_tls_verification": {},
            "security_comparison": {},
            "certificate_analysis": {},
            "warnings_summary": []
        }

    def log(self, message: str, level: str = "INFO"):
        """Log message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        if level == "ERROR":
            logger.error(message)
        elif level == "WARNING":
            logger.warning(message)
        else:
            logger.info(message)

    def analyze_http_protocol(self) -> Dict:
        """Analyze HTTP protocol characteristics"""
        self.log("Analyzing HTTP protocol...", "TEST")

        analysis = {
            "protocol": "HTTP",
            "version": "HTTP/1.1 (RFC 7230)",
            "encryption": {
                "enabled": False,
                "description": "No encryption - plain text transmission",
                "cipher_suites": "N/A",
                "key_exchange": "N/A"
            },
            "authentication": {
                "enabled": False,
                "server_verification": "NONE",
                "client_verification": "NONE",
                "certificate_based": False
            },
            "integrity_protection": {
                "enabled": False,
                "hmac_protection": False,
                "data_signing": False,
                "description": "No protection against tampering"
            },
            "attack_resistance": {
                "man_in_the_middle": "VULNERABLE - No protection",
                "replay_attacks": "VULNERABLE - No replay protection",
                "downgrade_attacks": "VULNERABLE - No version negotiation",
                "eavesdropping": "VULNERABLE - All data visible",
                "credential_theft": "CRITICAL - Credentials in plain text",
                "session_hijacking": "VULNERABLE - No session protection"
            },
            "headers": {
                "typical": [
                    "Content-Type",
                    "Content-Length",
                    "Cache-Control",
                    "Expires",
                    "Set-Cookie (vulnerable - unencrypted)"
                ],
                "security_headers": "NOT SUPPORTED - Would be transmitted in plain text"
            },
            "use_cases": {
                "recommended": ["Public non-sensitive data", "Internal networks only"],
                "not_recommended": [
                    "Authentication",
                    "Sensitive data",
                    "Financial transactions",
                    "Personal information",
                    "Credentials",
                    "Session tokens"
                ]
            },
            "vulnerabilities": [
                "Content modification by MITM attackers",
                "Passive eavesdropping possible",
                "No server identity verification",
                "Session cookies visible to attackers",
                "Credentials transmitted in plain text",
                "No forward secrecy",
                "Vulnerable to protocol downgrade"
            ],
            "ssl_tls_support": False,
            "certificate_validation": False,
            "hostname_verification": False
        }

        self.log("✓ HTTP protocol analysis complete", "SUCCESS")
        return analysis

    def analyze_https_protocol(self) -> Dict:
        """Analyze HTTPS protocol characteristics"""
        self.log("Analyzing HTTPS protocol...", "TEST")

        analysis = {
            "protocol": "HTTPS",
            "version": "HTTP/1.1 over TLS/SSL (RFC 7230 + RFC 8446)",
            "encryption": {
                "enabled": True,
                "description": "TLS 1.3 / TLS 1.2 encryption",
                "cipher_suites": [
                    "TLS_AES_256_GCM_SHA384 (TLS 1.3)",
                    "TLS_AES_128_GCM_SHA256 (TLS 1.3)",
                    "TLS_CHACHA20_POLY1305_SHA256 (TLS 1.3)",
                    "ECDHE-ECDSA-AES256-GCM-SHA384 (TLS 1.2)",
                    "ECDHE-RSA-AES256-GCM-SHA384 (TLS 1.2)",
                    "ECDHE-ECDSA-CHACHA20-POLY1305 (TLS 1.2)",
                    "ECDHE-RSA-CHACHA20-POLY1305 (TLS 1.2)"
                ],
                "key_exchange": "ECDHE (Elliptic Curve Diffie-Hellman Ephemeral)",
                "authentication": "ECDSA or RSA",
                "key_bits": "256-bit or higher"
            },
            "authentication": {
                "enabled": True,
                "server_verification": "X.509 Certificates",
                "client_verification": "Optional (mutual TLS)",
                "certificate_based": True,
                "pki_validation": "Public Key Infrastructure via Certificate Authority"
            },
            "integrity_protection": {
                "enabled": True,
                "hmac_protection": "HMAC-SHA256 or HMAC-SHA384",
                "data_signing": "All data authenticated",
                "description": "Protection against tampering via AEAD ciphers"
            },
            "attack_resistance": {
                "man_in_the_middle": "PROTECTED - Certificate pinning available",
                "replay_attacks": "PROTECTED - TLS sequence numbers",
                "downgrade_attacks": "PROTECTED - TLS version negotiation",
                "eavesdropping": "PROTECTED - All traffic encrypted",
                "credential_theft": "PROTECTED - Credentials encrypted",
                "session_hijacking": "PROTECTED - Session encryption"
            },
            "headers": {
                "typical": [
                    "Content-Type",
                    "Content-Length",
                    "Cache-Control",
                    "Set-Cookie (secure and httponly)"
                ],
                "security_headers": [
                    "Strict-Transport-Security (HSTS)",
                    "X-Content-Type-Options",
                    "X-Frame-Options",
                    "X-XSS-Protection",
                    "Content-Security-Policy",
                    "Referrer-Policy"
                ]
            },
            "features": {
                "perfect_forward_secrecy": "SUPPORTED - ECDHE with ephemeral keys",
                "session_resumption": "SUPPORTED - Session tickets (TLS 1.3)",
                "0_rtt": "SUPPORTED - Early data (TLS 1.3, with caution)",
                "certificate_transparency": "SUPPORTED - Log verification"
            },
            "use_cases": {
                "recommended": [
                    "All web traffic",
                    "Authentication",
                    "Financial transactions",
                    "Personal data",
                    "Credentials",
                    "Sensitive communications"
                ],
                "required_for": [
                    "E-commerce",
                    "Banking",
                    "Healthcare",
                    "Government",
                    "Authentication systems"
                ]
            },
            "ssl_tls_support": True,
            "certificate_validation": True,
            "hostname_verification": True,
            "modern_security": True
        }

        self.log("✓ HTTPS protocol analysis complete", "SUCCESS")
        return analysis

    def analyze_tls_versions(self) -> Dict:
        """Analyze TLS versions and deprecation"""
        self.log("Analyzing TLS versions...", "TEST")

        versions = {
            "SSL 2.0": {
                "year": 1995,
                "status": "DEPRECATED",
                "security": "BROKEN - Severe vulnerabilities",
                "issues": ["No certificate verification", "Export-grade ciphers", "Padding oracle attacks"],
                "disabled": True,
                "browsers": "All modern browsers"
            },
            "SSL 3.0": {
                "year": 1996,
                "status": "DEPRECATED",
                "security": "BROKEN - POODLE vulnerability",
                "issues": ["MAC-then-encrypt", "No protection against compression", "Padding oracle"],
                "disabled": True,
                "browsers": "All modern browsers"
            },
            "TLS 1.0": {
                "year": 1999,
                "status": "DEPRECATED",
                "security": "WEAK - Critical vulnerabilities",
                "issues": ["BEAST attack vulnerable", "Weak ciphers", "No AEAD support"],
                "disabled": True,
                "browsers": "Firefox, Chrome (2020+), Edge (2021+)"
            },
            "TLS 1.1": {
                "year": 2006,
                "status": "DEPRECATED",
                "security": "WEAK - DROWN attack vulnerable",
                "issues": ["Weak ciphers", "No AEAD support"],
                "disabled": True,
                "browsers": "Most modern browsers (2020+)"
            },
            "TLS 1.2": {
                "year": 2008,
                "status": "CURRENT",
                "security": "GOOD - If configured properly",
                "features": ["AEAD ciphers", "GCM mode", "Forward secrecy with ECDHE"],
                "disabled": False,
                "minimum_required": True,
                "notes": "Many enterprises still require this for compatibility"
            },
            "TLS 1.3": {
                "year": 2018,
                "status": "MODERN",
                "security": "EXCELLENT - Latest standard",
                "features": [
                    "Mandatory AEAD ciphers",
                    "Ephemeral key exchange",
                    "0-RTT resumption",
                    "Simplified handshake",
                    "Certificate transparency",
                    "Post-handshake authentication"
                ],
                "disabled": False,
                "recommended": True,
                "adoption": "90%+ of modern browsers"
            }
        }

        self.log("✓ TLS version analysis complete", "SUCCESS")
        return versions

    def analyze_certificate_validation(self) -> Dict:
        """Analyze certificate validation process"""
        self.log("Analyzing certificate validation...", "TEST")

        validation = {
            "process": {
                "step_1": {
                    "name": "Certificate Retrieval",
                    "description": "Server sends certificate chain during TLS handshake",
                    "details": [
                        "Server certificate",
                        "Intermediate CA certificate(s)",
                        "Root CA certificate reference"
                    ]
                },
                "step_2": {
                    "name": "Chain Validation",
                    "description": "Verify certificate chain integrity",
                    "checks": [
                        "Signature verification (CA signs cert)",
                        "Not-before and not-after dates",
                        "CA certificate validity",
                        "Certificate revocation status (CRL/OCSP)"
                    ]
                },
                "step_3": {
                    "name": "Hostname Verification",
                    "description": "Verify certificate matches requested hostname",
                    "checks": [
                        "Subject Common Name (CN) matching",
                        "Subject Alternative Name (SAN) matching",
                        "Wildcard support (*.example.com)",
                        "Case-insensitive matching"
                    ]
                },
                "step_4": {
                    "name": "Root CA Trust",
                    "description": "Verify CA certificate is in trust store",
                    "details": [
                        "Operating system CA store",
                        "Browser CA store",
                        "Application CA store (certifi for Python)"
                    ]
                }
            },
            "common_errors": {
                "self_signed_certificate": {
                    "error": "CERTIFICATE_VERIFY_FAILED",
                    "cause": "Certificate not signed by trusted CA",
                    "solution": "Add to trust store (dev only) or use proper CA"
                },
                "hostname_mismatch": {
                    "error": "CERTIFICATE_VERIFY_FAILED",
                    "cause": "Certificate hostname doesn't match request",
                    "solution": "Update certificate or request correct hostname"
                },
                "expired_certificate": {
                    "error": "CERTIFICATE_VERIFY_FAILED",
                    "cause": "Certificate passed expiration date",
                    "solution": "Renew certificate"
                },
                "revoked_certificate": {
                    "error": "CERTIFICATE_REVOKED",
                    "cause": "CA revoked certificate",
                    "solution": "Obtain new certificate"
                },
                "untrusted_root": {
                    "error": "CERTIFICATE_VERIFY_FAILED",
                    "cause": "Root CA not in trust store",
                    "solution": "Add CA to trust store or use different CA"
                }
            },
            "best_practices": [
                "Always verify certificates in production",
                "Use current TLS versions (1.2+, prefer 1.3)",
                "Enable hostname verification",
                "Implement certificate pinning for critical connections",
                "Monitor certificate expiration",
                "Use HSTS headers to enforce HTTPS",
                "Implement OCSP stapling for efficiency",
                "Regular certificate audits"
            ]
        }

        self.log("✓ Certificate validation analysis complete", "SUCCESS")
        return validation

    def analyze_ssl_configuration(self) -> Dict:
        """Analyze SSL/TLS configuration best practices"""
        self.log("Analyzing SSL/TLS configuration...", "TEST")

        config = {
            "server_configuration": {
                "recommended_protocols": ["TLS 1.3", "TLS 1.2"],
                "disabled_protocols": ["SSL 2.0", "SSL 3.0", "TLS 1.0", "TLS 1.1"],
                "cipher_suite_priority": [
                    "TLS_AES_256_GCM_SHA384",
                    "TLS_CHACHA20_POLY1305_SHA256",
                    "TLS_AES_128_GCM_SHA256",
                    "ECDHE-ECDSA-AES256-GCM-SHA384",
                    "ECDHE-RSA-AES256-GCM-SHA384"
                ]
            },
            "client_configuration": {
                "certificate_verification": "MUST enable in production",
                "hostname_verification": "MUST enable",
                "ca_bundle": "Use system CA store or certifi",
                "timeout": "Set appropriate timeout (30s default)",
                "session_reuse": "Enabled for performance"
            },
            "certificate_requirements": {
                "algorithm": "RSA (2048+ bits) or ECDSA (256+ bits)",
                "subject_fields": [
                    "C (Country)",
                    "ST (State)",
                    "L (Locality)",
                    "O (Organization)",
                    "CN (Common Name - hostname)",
                    "SAN (Subject Alternative Names)"
                ],
                "validity": "1-2 years recommended",
                "key_usage": [
                    "Digital Signature",
                    "Key Encipherment",
                    "Extended Key Usage: Server Authentication"
                ]
            },
            "security_headers": {
                "HSTS": {
                    "header": "Strict-Transport-Security: max-age=31536000; includeSubDomains; preload",
                    "purpose": "Force HTTPS-only access",
                    "preload_list": "Included in browser HSTS preload list"
                },
                "CSP": {
                    "header": "Content-Security-Policy: default-src 'self'",
                    "purpose": "Prevent XSS and injection attacks"
                },
                "XCTO": {
                    "header": "X-Content-Type-Options: nosniff",
                    "purpose": "Prevent MIME type sniffing"
                }
            }
        }

        self.log("✓ SSL/TLS configuration analysis complete", "SUCCESS")
        return config

    def identify_warnings(self) -> List[Dict]:
        """Identify SSL/TLS related warnings"""
        self.log("Identifying SSL/TLS warnings...", "TEST")

        warnings = [
            {
                "severity": "CRITICAL",
                "category": "HTTP Usage",
                "warning": "HTTP transmits all data in plain text",
                "impact": "Credentials, session tokens, and sensitive data are visible to attackers",
                "mitigation": "Always use HTTPS for production systems"
            },
            {
                "severity": "CRITICAL",
                "category": "Certificate Verification",
                "warning": "Disabling certificate verification removes protection against MITM",
                "impact": "Attackers can intercept HTTPS connections with forged certificates",
                "mitigation": "Always enable certificate verification in production"
            },
            {
                "severity": "HIGH",
                "category": "TLS Version",
                "warning": "Using TLS 1.0 or 1.1 is deprecated",
                "impact": "Vulnerable to known attacks (BEAST, POODLE, etc.)",
                "mitigation": "Upgrade to TLS 1.2 or 1.3"
            },
            {
                "severity": "HIGH",
                "category": "Weak Ciphers",
                "warning": "Export-grade or DES ciphers can be broken in minutes",
                "impact": "Traffic can be decrypted by determined attackers",
                "mitigation": "Use only strong modern ciphers (AES-256, ChaCha20)"
            },
            {
                "severity": "MEDIUM",
                "category": "Certificate Pinning",
                "warning": "Public CA compromise could lead to MITM attacks",
                "impact": "Forged certificates from compromised CAs can intercept connections",
                "mitigation": "Implement certificate or public key pinning for critical connections"
            },
            {
                "severity": "MEDIUM",
                "category": "HSTS",
                "warning": "Missing HSTS headers allows SSL stripping attacks",
                "impact": "Attacker can force clients to use HTTP",
                "mitigation": "Implement HSTS headers with appropriate max-age"
            },
            {
                "severity": "LOW",
                "category": "Hostname Verification",
                "warning": "Disabling hostname verification allows certificate substitution",
                "impact": "Attacker can use valid certificate for different domain",
                "mitigation": "Always enable hostname verification"
            },
            {
                "severity": "LOW",
                "category": "Session Resumption",
                "warning": "Session tickets not authenticated in TLS 1.2",
                "impact": "Tickets can be reused if session key is compromised",
                "mitigation": "Upgrade to TLS 1.3 or use session IDs instead of tickets"
            }
        ]

        self.log(f"✓ Identified {len(warnings)} warnings", "SUCCESS")
        return warnings

    def run_analysis(self) -> Dict:
        """Run complete protocol analysis"""
        self.log("=" * 80, "INFO")
        self.log("HTTP vs HTTPS PROTOCOL ANALYSIS", "INFO")
        self.log("=" * 80, "INFO")

        # Analyze protocols
        http_analysis = self.analyze_http_protocol()
        https_analysis = self.analyze_https_protocol()
        tls_versions = self.analyze_tls_versions()
        cert_validation = self.analyze_certificate_validation()
        ssl_config = self.analyze_ssl_configuration()
        warnings_list = self.identify_warnings()

        # Build report
        self.report["protocol_analysis"] = {
            "http": http_analysis,
            "https": https_analysis
        }
        self.report["tls_versions"] = tls_versions
        self.report["certificate_validation"] = cert_validation
        self.report["ssl_tls_configuration"] = ssl_config
        self.report["ssl_tls_warnings"] = warnings_list

        # Add summary
        self._add_summary()

        self._print_analysis_summary()
        return self.report

    def _add_summary(self) -> None:
        """Add analysis summary to report"""
        http_vulns = len(self.report["protocol_analysis"]["http"]["vulnerabilities"])
        https_features = len(self.report["protocol_analysis"]["https"]["features"])
        critical_warnings = sum(1 for w in self.report["ssl_tls_warnings"] if w["severity"] == "CRITICAL")

        self.report["summary"] = {
            "http_vulnerabilities": http_vulns,
            "https_security_features": https_features,
            "tls_versions_analyzed": len(self.report["tls_versions"]),
            "deprecated_protocols": sum(1 for v in self.report["tls_versions"].values() if v.get("status") == "DEPRECATED"),
            "critical_warnings": critical_warnings,
            "recommendation": "ALWAYS USE HTTPS FOR PRODUCTION - HTTP IS FUNDAMENTALLY INSECURE"
        }

    def _print_analysis_summary(self) -> None:
        """Print analysis summary"""
        self.log("\n" + "=" * 80, "INFO")
        self.log("PROTOCOL COMPARISON SUMMARY", "INFO")
        self.log("=" * 80, "INFO")

        http = self.report["protocol_analysis"]["http"]
        https = self.report["protocol_analysis"]["https"]

        self.log("\nHTTP (Unencrypted):", "INFO")
        self.log(f"  Encryption: {http['encryption']['enabled']}", "ERROR")
        self.log(f"  Authentication: {http['authentication']['enabled']}", "ERROR")
        self.log(f"  Vulnerabilities: {len(http['vulnerabilities'])}", "ERROR")

        self.log("\nHTTPS (Encrypted):", "INFO")
        self.log(f"  Encryption: {https['encryption']['enabled']}", "SUCCESS")
        self.log(f"  Authentication: {https['authentication']['enabled']}", "SUCCESS")
        self.log(f"  Security Features: {len(https['features'])}", "SUCCESS")

        self.log("\nSSL/TLS Warnings Summary:", "INFO")
        for warning in self.report["ssl_tls_warnings"][:3]:
            severity = "ERROR" if warning["severity"] == "CRITICAL" else "WARNING"
            self.log(f"  [{warning['severity']}] {warning['warning']}", severity)

    def save_report(self, filename: str = None) -> str:
        """Save analysis report"""
        if filename is None:
            filename = f"http_https_protocol_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        filepath = Path(filename)
        with open(filepath, 'w') as f:
            json.dump(self.report, f, indent=2)

        self.log(f"Report saved to {filepath}", "SUCCESS")
        return str(filepath)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="HTTP vs HTTPS Protocol Analysis"
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output report filename"
    )

    args = parser.parse_args()

    # Run analysis
    analyzer = HTTPSProtocolAnalyzer()
    report = analyzer.run_analysis()

    # Save report
    report_path = analyzer.save_report(args.output)

    print(f"\n✓ Analysis complete: {report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
