#!/usr/bin/env python3
"""
TLS Certificate Pinning for C2 Proxy Connections

Implements certificate pinning, public key pinning, and pin validation
to prevent MITM attacks on C2 proxy connections during authorized pentesting.

Features:
- Public Key Infrastructure (PKI) pinning
- Certificate hash pinning (SHA-256)
- Subject Public Key Info (SPKI) pinning
- Certificate chain validation
- Pin expiration and rotation
- Fallback certificate handling
- Pin backup and restoration
- Security audit logging

For authorized pentesting and security research only.
"""

import ssl
import socket
import hashlib
import json
import os
import logging
import threading
import time
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
from cryptography import x509
from cryptography.x509.oid import ExtensionOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
import certifi
import urllib.request
import urllib.error

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PinningStrategy(Enum):
    """TLS pinning strategies"""
    CERTIFICATE = "certificate"        # Pin entire certificate
    PUBLIC_KEY = "public_key"          # Pin public key
    SPKI = "spki"                      # Pin SPKI (Subject Public Key Info)
    CHAIN = "chain"                    # Pin entire certificate chain
    BACKUP = "backup"                  # Pin backup certificates


class HashAlgorithm(Enum):
    """Hash algorithms for pinning"""
    SHA256 = "sha256"
    SHA384 = "sha384"
    SHA512 = "sha512"


@dataclass
class PinData:
    """Individual pin configuration"""
    pin_id: str
    strategy: PinningStrategy
    pin_hash: str
    hash_algorithm: HashAlgorithm
    subject_name: str = ""
    issuer_name: str = ""
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    expires_at: Optional[str] = None
    backup_pins: List[str] = field(default_factory=list)
    is_active: bool = True
    notes: str = ""

    def is_expired(self) -> bool:
        """Check if pin has expired"""
        if not self.expires_at:
            return False
        expiry = datetime.fromisoformat(self.expires_at)
        return datetime.utcnow() > expiry

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'pin_id': self.pin_id,
            'strategy': self.strategy.value,
            'pin_hash': self.pin_hash,
            'hash_algorithm': self.hash_algorithm.value,
            'subject_name': self.subject_name,
            'issuer_name': self.issuer_name,
            'created_at': self.created_at,
            'expires_at': self.expires_at,
            'backup_pins': self.backup_pins,
            'is_active': self.is_active,
            'notes': self.notes
        }

    @staticmethod
    def from_dict(data: Dict) -> 'PinData':
        """Create from dictionary"""
        return PinData(
            pin_id=data['pin_id'],
            strategy=PinningStrategy(data['strategy']),
            pin_hash=data['pin_hash'],
            hash_algorithm=HashAlgorithm(data['hash_algorithm']),
            subject_name=data.get('subject_name', ''),
            issuer_name=data.get('issuer_name', ''),
            created_at=data.get('created_at', datetime.utcnow().isoformat()),
            expires_at=data.get('expires_at'),
            backup_pins=data.get('backup_pins', []),
            is_active=data.get('is_active', True),
            notes=data.get('notes', '')
        )


@dataclass
class PinningValidationResult:
    """Result of pin validation"""
    is_valid: bool
    strategy_used: PinningStrategy
    matched_pin_id: str = ""
    certificate_hash: str = ""
    chain_depth: int = 0
    validation_timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    error_message: str = ""
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


class CertificateExtractor:
    """Extract and process certificates from remote servers"""

    @staticmethod
    def get_server_certificate(
        host: str,
        port: int,
        timeout: float = 10.0
    ) -> Optional[x509.Certificate]:
        """
        Retrieve server certificate from remote host

        Args:
            host: Server hostname
            port: Server port
            timeout: Connection timeout in seconds

        Returns:
            x509.Certificate object or None
        """
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            with socket.create_connection((host, port), timeout=timeout) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    cert_der = ssock.getpeercert(binary_form=True)

            if not cert_der:
                logger.error(f"Failed to retrieve certificate from {host}:{port}")
                return None

            # Parse DER certificate
            cert = x509.load_der_x509_certificate(cert_der, default_backend())
            logger.info(f"Successfully retrieved certificate from {host}:{port}")
            return cert

        except socket.timeout:
            logger.error(f"Connection timeout while retrieving certificate from {host}:{port}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving certificate from {host}:{port}: {e}")
            return None

    @staticmethod
    def get_certificate_chain(
        host: str,
        port: int,
        timeout: float = 10.0
    ) -> List[x509.Certificate]:
        """
        Retrieve full certificate chain from server

        Args:
            host: Server hostname
            port: Server port
            timeout: Connection timeout in seconds

        Returns:
            List of x509.Certificate objects
        """
        chain = []
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            with socket.create_connection((host, port), timeout=timeout) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    peer_cert_chain = ssock.getpeercert_chain()

            for cert_der in peer_cert_chain:
                try:
                    cert = x509.load_der_x509_certificate(cert_der, default_backend())
                    chain.append(cert)
                except Exception as e:
                    logger.warning(f"Failed to parse certificate in chain: {e}")

            logger.info(f"Retrieved certificate chain of depth {len(chain)} from {host}:{port}")
            return chain

        except Exception as e:
            logger.error(f"Error retrieving certificate chain from {host}:{port}: {e}")
            return []

    @staticmethod
    def extract_public_key(cert: x509.Certificate) -> Optional[bytes]:
        """
        Extract public key from certificate

        Args:
            cert: x509.Certificate object

        Returns:
            DER-encoded public key bytes or None
        """
        try:
            public_key = cert.public_key()
            public_key_der = public_key.public_key_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            return public_key_der
        except Exception as e:
            logger.error(f"Error extracting public key: {e}")
            return None

    @staticmethod
    def extract_spki(cert: x509.Certificate) -> Optional[bytes]:
        """
        Extract Subject Public Key Info (SPKI) from certificate

        Args:
            cert: x509.Certificate object

        Returns:
            DER-encoded SPKI bytes or None
        """
        return CertificateExtractor.extract_public_key(cert)

    @staticmethod
    def get_certificate_info(cert: x509.Certificate) -> Dict:
        """
        Extract certificate metadata

        Args:
            cert: x509.Certificate object

        Returns:
            Dictionary with certificate information
        """
        try:
            subject_name = cert.subject.rfc4514_string()
            issuer_name = cert.issuer.rfc4514_string()
            serial_number = str(cert.serial_number)
            not_valid_before = cert.not_valid_before.isoformat()
            not_valid_after = cert.not_valid_after.isoformat()

            # Extract SANs
            try:
                san_ext = cert.extensions.get_extension_for_oid(
                    ExtensionOID.SUBJECT_ALTERNATIVE_NAME
                )
                san_names = [name.value for name in san_ext.value]
            except x509.ExtensionNotFound:
                san_names = []

            return {
                'subject_name': subject_name,
                'issuer_name': issuer_name,
                'serial_number': serial_number,
                'not_valid_before': not_valid_before,
                'not_valid_after': not_valid_after,
                'subject_alternative_names': san_names,
                'version': cert.version.name
            }
        except Exception as e:
            logger.error(f"Error extracting certificate info: {e}")
            return {}


class PinHashGenerator:
    """Generate hash pins for certificates and keys"""

    @staticmethod
    def hash_data(
        data: bytes,
        algorithm: HashAlgorithm = HashAlgorithm.SHA256
    ) -> str:
        """
        Generate hash of data

        Args:
            data: Data to hash
            algorithm: Hash algorithm to use

        Returns:
            Hexadecimal hash string
        """
        if algorithm == HashAlgorithm.SHA256:
            return hashlib.sha256(data).hexdigest()
        elif algorithm == HashAlgorithm.SHA384:
            return hashlib.sha384(data).hexdigest()
        elif algorithm == HashAlgorithm.SHA512:
            return hashlib.sha512(data).hexdigest()
        else:
            return hashlib.sha256(data).hexdigest()

    @staticmethod
    def pin_certificate(
        cert: x509.Certificate,
        algorithm: HashAlgorithm = HashAlgorithm.SHA256
    ) -> str:
        """
        Generate pin hash for entire certificate

        Args:
            cert: x509.Certificate object
            algorithm: Hash algorithm

        Returns:
            Hash pin string
        """
        cert_der = cert.public_bytes(serialization.Encoding.DER)
        return PinHashGenerator.hash_data(cert_der, algorithm)

    @staticmethod
    def pin_public_key(
        cert: x509.Certificate,
        algorithm: HashAlgorithm = HashAlgorithm.SHA256
    ) -> str:
        """
        Generate pin hash for public key

        Args:
            cert: x509.Certificate object
            algorithm: Hash algorithm

        Returns:
            Hash pin string
        """
        public_key_der = CertificateExtractor.extract_public_key(cert)
        if not public_key_der:
            raise ValueError("Failed to extract public key")
        return PinHashGenerator.hash_data(public_key_der, algorithm)

    @staticmethod
    def pin_spki(
        cert: x509.Certificate,
        algorithm: HashAlgorithm = HashAlgorithm.SHA256
    ) -> str:
        """
        Generate pin hash for SPKI

        Args:
            cert: x509.Certificate object
            algorithm: Hash algorithm

        Returns:
            Hash pin string
        """
        spki_der = CertificateExtractor.extract_spki(cert)
        if not spki_der:
            raise ValueError("Failed to extract SPKI")
        return PinHashGenerator.hash_data(spki_der, algorithm)


class TLSPinningValidator:
    """Validate TLS certificates against pins"""

    def __init__(self, pin_database: Dict[str, PinData]):
        """
        Initialize validator with pin database

        Args:
            pin_database: Dictionary mapping hosts to PinData objects
        """
        self.pin_database = pin_database
        self.lock = threading.Lock()

    def validate_certificate_pin(
        self,
        cert: x509.Certificate,
        pin: PinData,
        cert_der: Optional[bytes] = None
    ) -> bool:
        """
        Validate certificate against pin

        Args:
            cert: x509.Certificate to validate
            pin: PinData to validate against
            cert_der: Optional pre-extracted DER certificate

        Returns:
            True if certificate matches pin
        """
        try:
            if pin.strategy == PinningStrategy.CERTIFICATE:
                if not cert_der:
                    cert_der = cert.public_bytes(serialization.Encoding.DER)
                cert_hash = PinHashGenerator.hash_data(cert_der, pin.hash_algorithm)
                return cert_hash == pin.pin_hash

            elif pin.strategy == PinningStrategy.PUBLIC_KEY:
                key_hash = PinHashGenerator.pin_public_key(cert, pin.hash_algorithm)
                return key_hash == pin.pin_hash

            elif pin.strategy == PinningStrategy.SPKI:
                spki_hash = PinHashGenerator.pin_spki(cert, pin.hash_algorithm)
                return spki_hash == pin.pin_hash

            else:
                logger.warning(f"Unknown pinning strategy: {pin.strategy}")
                return False

        except Exception as e:
            logger.error(f"Error validating pin: {e}")
            return False

    def validate_chain_pin(
        self,
        cert_chain: List[x509.Certificate],
        pin: PinData
    ) -> bool:
        """
        Validate certificate chain against pin

        Args:
            cert_chain: List of x509.Certificate objects
            pin: PinData to validate against

        Returns:
            True if any certificate in chain matches pin
        """
        if pin.strategy != PinningStrategy.CHAIN:
            return False

        for cert in cert_chain:
            if self.validate_certificate_pin(cert, pin):
                return True

        return False

    def validate_certificate_against_pins(
        self,
        cert: x509.Certificate,
        host: str,
        cert_chain: Optional[List[x509.Certificate]] = None,
        cert_der: Optional[bytes] = None
    ) -> PinningValidationResult:
        """
        Validate certificate against all applicable pins

        Args:
            cert: x509.Certificate to validate
            host: Server hostname
            cert_chain: Optional certificate chain
            cert_der: Optional pre-extracted DER certificate

        Returns:
            PinningValidationResult object
        """
        with self.lock:
            if host not in self.pin_database:
                return PinningValidationResult(
                    is_valid=False,
                    strategy_used=PinningStrategy.CERTIFICATE,
                    error_message=f"No pins configured for host: {host}"
                )

            pins = self.pin_database[host]
            if isinstance(pins, PinData):
                pins = [pins]
            else:
                pins = pins if isinstance(pins, list) else list(pins.values())

            # Filter active, non-expired pins
            valid_pins = [
                p for p in pins
                if p.is_active and not p.is_expired()
            ]

            if not valid_pins:
                return PinningValidationResult(
                    is_valid=False,
                    strategy_used=PinningStrategy.CERTIFICATE,
                    error_message=f"No valid pins for host: {host}"
                )

            # Try primary pins
            for pin in valid_pins:
                if pin.strategy == PinningStrategy.CHAIN and cert_chain:
                    if self.validate_chain_pin(cert_chain, pin):
                        return PinningValidationResult(
                            is_valid=True,
                            strategy_used=pin.strategy,
                            matched_pin_id=pin.pin_id,
                            certificate_hash=pin.pin_hash,
                            chain_depth=len(cert_chain)
                        )
                else:
                    if self.validate_certificate_pin(cert, pin, cert_der):
                        return PinningValidationResult(
                            is_valid=True,
                            strategy_used=pin.strategy,
                            matched_pin_id=pin.pin_id,
                            certificate_hash=pin.pin_hash
                        )

            # Try backup pins
            for pin in valid_pins:
                if pin.backup_pins:
                    for backup_pin_hash in pin.backup_pins:
                        if pin.strategy == PinningStrategy.CERTIFICATE:
                            if not cert_der:
                                cert_der = cert.public_bytes(serialization.Encoding.DER)
                            cert_hash = PinHashGenerator.hash_data(cert_der, pin.hash_algorithm)
                            if cert_hash == backup_pin_hash:
                                return PinningValidationResult(
                                    is_valid=True,
                                    strategy_used=pin.strategy,
                                    matched_pin_id=pin.pin_id,
                                    certificate_hash=backup_pin_hash,
                                    warnings=["Matched backup pin, consider updating"]
                                )

            return PinningValidationResult(
                is_valid=False,
                strategy_used=valid_pins[0].strategy if valid_pins else PinningStrategy.CERTIFICATE,
                error_message="Certificate does not match any valid pins"
            )


class TLSPinningManager:
    """Manage TLS certificate pins for C2 connections"""

    def __init__(self, config_dir: str = '/tmp/sc-pins'):
        """
        Initialize pinning manager

        Args:
            config_dir: Directory for pin storage
        """
        self.config_dir = config_dir
        os.makedirs(config_dir, exist_ok=True)

        self.pins: Dict[str, List[PinData]] = {}
        self.validator: TLSPinningValidator = TLSPinningValidator(self.pins)
        self.lock = threading.Lock()
        self.audit_log: List[Dict] = []

        self._load_pins()

    def _load_pins(self):
        """Load pins from disk"""
        pin_file = os.path.join(self.config_dir, 'pins.json')
        if os.path.exists(pin_file):
            try:
                with open(pin_file, 'r') as f:
                    data = json.load(f)
                    for host, pins_data in data.items():
                        self.pins[host] = [
                            PinData.from_dict(p) for p in pins_data
                        ]
                logger.info(f"Loaded pins for {len(self.pins)} hosts")
            except Exception as e:
                logger.error(f"Error loading pins: {e}")

    def _save_pins(self):
        """Save pins to disk"""
        pin_file = os.path.join(self.config_dir, 'pins.json')
        with self.lock:
            data = {
                host: [p.to_dict() for p in pins]
                for host, pins in self.pins.items()
            }
        with open(pin_file, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved pins for {len(self.pins)} hosts")

    def add_pin_from_certificate(
        self,
        host: str,
        cert: x509.Certificate,
        strategy: PinningStrategy = PinningStrategy.PUBLIC_KEY,
        hash_algorithm: HashAlgorithm = HashAlgorithm.SHA256,
        expiration_days: Optional[int] = None,
        backup_pins: Optional[List[str]] = None,
        notes: str = ""
    ) -> str:
        """
        Add pin from certificate

        Args:
            host: Server hostname
            cert: x509.Certificate to pin
            strategy: Pinning strategy to use
            hash_algorithm: Hash algorithm
            expiration_days: Days until pin expires
            backup_pins: List of backup pin hashes
            notes: Additional notes

        Returns:
            Pin ID
        """
        import uuid
        pin_id = f"pin_{uuid.uuid4().hex[:12]}"

        # Generate pin hash
        if strategy == PinningStrategy.CERTIFICATE:
            pin_hash = PinHashGenerator.pin_certificate(cert, hash_algorithm)
        elif strategy == PinningStrategy.PUBLIC_KEY:
            pin_hash = PinHashGenerator.pin_public_key(cert, hash_algorithm)
        elif strategy == PinningStrategy.SPKI:
            pin_hash = PinHashGenerator.pin_spki(cert, hash_algorithm)
        else:
            raise ValueError(f"Unsupported strategy: {strategy}")

        # Get certificate info
        cert_info = CertificateExtractor.get_certificate_info(cert)

        # Calculate expiration
        expires_at = None
        if expiration_days:
            expires_at = (
                datetime.utcnow() + timedelta(days=expiration_days)
            ).isoformat()

        # Create pin
        pin = PinData(
            pin_id=pin_id,
            strategy=strategy,
            pin_hash=pin_hash,
            hash_algorithm=hash_algorithm,
            subject_name=cert_info.get('subject_name', ''),
            issuer_name=cert_info.get('issuer_name', ''),
            expires_at=expires_at,
            backup_pins=backup_pins or [],
            notes=notes
        )

        with self.lock:
            if host not in self.pins:
                self.pins[host] = []
            self.pins[host].append(pin)

        self._save_pins()
        self._audit_log('pin_added', host, pin_id, f"Added {strategy.value} pin")
        logger.info(f"Added {strategy.value} pin for {host}: {pin_id}")
        return pin_id

    def add_pin_from_server(
        self,
        host: str,
        port: int = 443,
        strategy: PinningStrategy = PinningStrategy.PUBLIC_KEY,
        hash_algorithm: HashAlgorithm = HashAlgorithm.SHA256,
        expiration_days: Optional[int] = 365,
        backup_pins: Optional[List[str]] = None,
        notes: str = "",
        timeout: float = 10.0
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Add pin by connecting to remote server

        Args:
            host: Server hostname
            port: Server port
            strategy: Pinning strategy
            hash_algorithm: Hash algorithm
            expiration_days: Days until pin expires
            backup_pins: Backup pin hashes
            notes: Notes
            timeout: Connection timeout

        Returns:
            Tuple of (success, message, pin_id)
        """
        try:
            cert = CertificateExtractor.get_server_certificate(host, port, timeout)
            if not cert:
                return False, f"Failed to retrieve certificate from {host}:{port}", None

            pin_id = self.add_pin_from_certificate(
                host=host,
                cert=cert,
                strategy=strategy,
                hash_algorithm=hash_algorithm,
                expiration_days=expiration_days,
                backup_pins=backup_pins,
                notes=notes
            )
            return True, f"Successfully pinned certificate from {host}:{port}", pin_id

        except Exception as e:
            error_msg = f"Error pinning certificate: {e}"
            logger.error(error_msg)
            self._audit_log('pin_error', host, '', error_msg)
            return False, error_msg, None

    def add_chain_pin_from_server(
        self,
        host: str,
        port: int = 443,
        hash_algorithm: HashAlgorithm = HashAlgorithm.SHA256,
        expiration_days: Optional[int] = 365,
        timeout: float = 10.0
    ) -> Tuple[bool, str]:
        """
        Add pins for entire certificate chain

        Args:
            host: Server hostname
            port: Server port
            hash_algorithm: Hash algorithm
            expiration_days: Days until pins expire
            timeout: Connection timeout

        Returns:
            Tuple of (success, message)
        """
        try:
            chain = CertificateExtractor.get_certificate_chain(host, port, timeout)
            if not chain:
                return False, f"Failed to retrieve certificate chain from {host}:{port}"

            pin_count = 0
            for idx, cert in enumerate(chain):
                try:
                    self.add_pin_from_certificate(
                        host=f"{host}:chain:{idx}",
                        cert=cert,
                        strategy=PinningStrategy.PUBLIC_KEY,
                        hash_algorithm=hash_algorithm,
                        expiration_days=expiration_days,
                        notes=f"Chain certificate {idx}"
                    )
                    pin_count += 1
                except Exception as e:
                    logger.warning(f"Failed to pin chain certificate {idx}: {e}")

            message = f"Pinned {pin_count} certificates from chain ({len(chain)} total)"
            self._audit_log('chain_pin_added', host, '', message)
            return True, message

        except Exception as e:
            error_msg = f"Error pinning certificate chain: {e}"
            logger.error(error_msg)
            return False, error_msg

    def validate_connection(
        self,
        host: str,
        port: int = 443,
        timeout: float = 10.0
    ) -> PinningValidationResult:
        """
        Validate connection to server using pins

        Args:
            host: Server hostname
            port: Server port
            timeout: Connection timeout

        Returns:
            PinningValidationResult
        """
        try:
            cert = CertificateExtractor.get_server_certificate(host, port, timeout)
            if not cert:
                result = PinningValidationResult(
                    is_valid=False,
                    strategy_used=PinningStrategy.CERTIFICATE,
                    error_message=f"Failed to retrieve certificate from {host}:{port}"
                )
                self._audit_log('validation_error', host, '', result.error_message)
                return result

            cert_chain = CertificateExtractor.get_certificate_chain(host, port, timeout)
            cert_der = cert.public_bytes(serialization.Encoding.DER)

            result = self.validator.validate_certificate_against_pins(
                cert=cert,
                host=host,
                cert_chain=cert_chain,
                cert_der=cert_der
            )

            if result.is_valid:
                self._audit_log('validation_success', host, result.matched_pin_id, '')
            else:
                self._audit_log('validation_failed', host, '', result.error_message)

            return result

        except Exception as e:
            error_msg = f"Error validating connection: {e}"
            logger.error(error_msg)
            self._audit_log('validation_error', host, '', error_msg)
            return PinningValidationResult(
                is_valid=False,
                strategy_used=PinningStrategy.CERTIFICATE,
                error_message=error_msg
            )

    def remove_pin(self, host: str, pin_id: str) -> Tuple[bool, str]:
        """
        Remove a pin

        Args:
            host: Server hostname
            pin_id: Pin ID to remove

        Returns:
            Tuple of (success, message)
        """
        with self.lock:
            if host not in self.pins:
                return False, f"No pins for host: {host}"

            original_count = len(self.pins[host])
            self.pins[host] = [p for p in self.pins[host] if p.pin_id != pin_id]

            if len(self.pins[host]) == original_count:
                return False, f"Pin {pin_id} not found"

            if not self.pins[host]:
                del self.pins[host]

        self._save_pins()
        self._audit_log('pin_removed', host, pin_id, '')
        logger.info(f"Removed pin {pin_id} for {host}")
        return True, "Pin removed successfully"

    def rotate_pins(
        self,
        host: str,
        port: int = 443,
        strategy: PinningStrategy = PinningStrategy.PUBLIC_KEY,
        hash_algorithm: HashAlgorithm = HashAlgorithm.SHA256,
        expiration_days: int = 365,
        timeout: float = 10.0
    ) -> Tuple[bool, str]:
        """
        Rotate pins for a host (backup old, add new)

        Args:
            host: Server hostname
            port: Server port
            strategy: Pinning strategy
            hash_algorithm: Hash algorithm
            expiration_days: Days until new pin expires
            timeout: Connection timeout

        Returns:
            Tuple of (success, message)
        """
        try:
            # Get current pins as backup
            backup_hashes = []
            with self.lock:
                if host in self.pins:
                    backup_hashes = [p.pin_hash for p in self.pins[host]]

            # Get new certificate and create pin
            success, message, pin_id = self.add_pin_from_server(
                host=host,
                port=port,
                strategy=strategy,
                hash_algorithm=hash_algorithm,
                expiration_days=expiration_days,
                backup_pins=backup_hashes,
                notes="Rotated pin",
                timeout=timeout
            )

            if success:
                self._audit_log('pin_rotated', host, pin_id, f"Rotated {len(backup_hashes)} backup pins")
                logger.info(f"Successfully rotated pins for {host}")
            else:
                logger.error(f"Failed to rotate pins for {host}: {message}")

            return success, message

        except Exception as e:
            error_msg = f"Error rotating pins: {e}"
            logger.error(error_msg)
            self._audit_log('rotation_error', host, '', error_msg)
            return False, error_msg

    def get_pins(self, host: str) -> List[Dict]:
        """Get all pins for a host"""
        with self.lock:
            if host not in self.pins:
                return []
            return [p.to_dict() for p in self.pins[host]]

    def get_all_pins(self) -> Dict[str, List[Dict]]:
        """Get all pins for all hosts"""
        with self.lock:
            return {
                host: [p.to_dict() for p in pins]
                for host, pins in self.pins.items()
            }

    def _audit_log(self, event_type: str, host: str, pin_id: str, details: str):
        """Log security audit event"""
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'host': host,
            'pin_id': pin_id,
            'details': details
        }
        self.audit_log.append(event)
        logger.debug(f"Audit: {event_type} - {host} - {pin_id}")

    def export_audit_log(self, output_file: Optional[str] = None) -> List[Dict]:
        """Export audit log"""
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(self.audit_log, f, indent=2)
            logger.info(f"Exported audit log to {output_file}")
        return self.audit_log

    def get_statistics(self) -> Dict:
        """Get pinning statistics"""
        with self.lock:
            total_pins = sum(len(pins) for pins in self.pins.values())
            active_pins = sum(
                sum(1 for p in pins if p.is_active and not p.is_expired())
                for pins in self.pins.values()
            )
            expired_pins = total_pins - active_pins

        return {
            'total_hosts': len(self.pins),
            'total_pins': total_pins,
            'active_pins': active_pins,
            'expired_pins': expired_pins,
            'audit_events': len(self.audit_log)
        }

    def export_report(self, output_file: Optional[str] = None) -> Dict:
        """Export comprehensive report"""
        report = {
            'generated_at': datetime.utcnow().isoformat(),
            'statistics': self.get_statistics(),
            'pins_by_host': self.get_all_pins(),
            'recent_audit_events': self.audit_log[-50:]  # Last 50 events
        }

        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"Exported report to {output_file}")

        return report


class HTTPSConnectionWithPinning:
    """HTTPS connection with TLS certificate pinning"""

    def __init__(self, pinning_manager: TLSPinningManager):
        """
        Initialize connection handler

        Args:
            pinning_manager: TLSPinningManager instance
        """
        self.pinning_manager = pinning_manager
        self.lock = threading.Lock()

    def make_pinned_request(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        data: Optional[bytes] = None,
        timeout: float = 10.0,
        verify_pins: bool = True
    ) -> Tuple[bool, Optional[str], Optional[Exception]]:
        """
        Make HTTPS request with pin validation

        Args:
            url: Target URL
            method: HTTP method
            headers: Request headers
            data: Request body
            timeout: Connection timeout
            verify_pins: Whether to verify pins

        Returns:
            Tuple of (success, response_text, error)
        """
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            host = parsed.hostname
            port = parsed.port or 443

            # Validate pins before connecting
            if verify_pins:
                result = self.pinning_manager.validate_connection(host, port, timeout)
                if not result.is_valid:
                    error = Exception(f"Pin validation failed: {result.error_message}")
                    logger.error(f"Pin validation failed for {host}: {result.error_message}")
                    return False, None, error

            # Make request
            headers = headers or {}
            headers['User-Agent'] = 'TLSPinningClient/1.0'

            req = urllib.request.Request(url, data=data, headers=headers, method=method)

            with urllib.request.urlopen(req, timeout=timeout) as response:
                response_text = response.read().decode('utf-8')
                logger.info(f"Successfully connected to {host}:{port} with pin validation")
                return True, response_text, None

        except Exception as e:
            logger.error(f"Error making pinned request: {e}")
            return False, None, e


# Example usage and testing
if __name__ == "__main__":
    print("=" * 80)
    print("TLS CERTIFICATE PINNING FOR C2 PROXY CONNECTIONS")
    print("=" * 80)

    # Initialize manager
    manager = TLSPinningManager()

    print("\n1. TLS Pinning Manager Initialized")
    print("-" * 80)
    print(f"  Configuration directory: {manager.config_dir}")

    # Example of adding pins
    print("\n2. Example Pin Management")
    print("-" * 80)
    print("""
    # Add pin from remote server:
    success, msg, pin_id = manager.add_pin_from_server(
        host='c2.example.com',
        port=443,
        strategy=PinningStrategy.PUBLIC_KEY,
        hash_algorithm=HashAlgorithm.SHA256,
        expiration_days=365,
        notes='C2 proxy primary handler'
    )

    # Validate connection:
    result = manager.validate_connection('c2.example.com', 443)
    if result.is_valid:
        print(f'Pin validation passed: {result.matched_pin_id}')
    else:
        print(f'Pin validation failed: {result.error_message}')

    # Rotate pins:
    success, msg = manager.rotate_pins('c2.example.com')

    # Export report:
    manager.export_report('/tmp/pinning_report.json')
    """)

    # Display statistics
    print("\n3. Pin Statistics")
    print("-" * 80)
    stats = manager.get_statistics()
    print(f"  Total hosts with pins: {stats['total_hosts']}")
    print(f"  Total pins: {stats['total_pins']}")
    print(f"  Active pins: {stats['active_pins']}")
    print(f"  Expired pins: {stats['expired_pins']}")
    print(f"  Audit events: {stats['audit_events']}")

    print("\n" + "=" * 80)
    print("TLS PINNING IMPLEMENTATION READY FOR USE")
    print("=" * 80)
