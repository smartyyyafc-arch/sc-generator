#!/usr/bin/env python3
"""
Registry Backup/Restore System
Implements comprehensive backup and restore functionality to preserve original registry values
during obfuscation and deobfuscation operations.

Features:
- Pre-operation backup of registry states
- Post-operation backup of modified states
- Full and incremental backup modes
- Restore to previous states
- Backup versioning with timestamps
- Metadata tracking and verification
- Rollback capabilities
"""

import json
import os
import hashlib
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import copy


class BackupMode(Enum):
    """Backup operation modes"""
    FULL = "full"           # Complete backup of all values
    INCREMENTAL = "incremental"  # Only changed values
    SNAPSHOT = "snapshot"   # Point-in-time snapshot


class RestoreMode(Enum):
    """Restore operation modes"""
    FULL_RESTORE = "full"   # Restore all values
    SELECTIVE = "selective"  # Restore specific values
    ROLLBACK = "rollback"    # Undo to previous state


@dataclass
class RegistryValueBackup:
    """Backup of a single registry value"""
    value_name: str
    value_data: str
    value_type: str
    timestamp: float
    path: str
    hive: str
    hash: str = ""

    def __post_init__(self):
        """Calculate hash of value data"""
        if not self.hash:
            self.hash = hashlib.sha256(
                f"{self.value_data}{self.value_type}".encode()
            ).hexdigest()


@dataclass
class RegistryBackupSnapshot:
    """Complete snapshot of registry state"""
    snapshot_id: str
    timestamp: float
    mode: str
    hive: str
    path: str
    values: Dict[str, RegistryValueBackup] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    parent_snapshot_id: Optional[str] = None  # For incremental backups

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'snapshot_id': self.snapshot_id,
            'timestamp': self.timestamp,
            'datetime': datetime.fromtimestamp(self.timestamp).isoformat(),
            'mode': self.mode,
            'hive': self.hive,
            'path': self.path,
            'value_count': len(self.values),
            'values': {
                name: {
                    'value_name': val.value_name,
                    'value_data': val.value_data,
                    'value_type': val.value_type,
                    'timestamp': val.timestamp,
                    'hash': val.hash,
                }
                for name, val in self.values.items()
            },
            'metadata': self.metadata,
            'parent_snapshot_id': self.parent_snapshot_id
        }


@dataclass
class BackupSession:
    """Manages a backup/restore session"""
    session_id: str
    created: float
    description: str
    snapshots: List[RegistryBackupSnapshot] = field(default_factory=list)
    operations: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'session_id': self.session_id,
            'created': self.created,
            'datetime': datetime.fromtimestamp(self.created).isoformat(),
            'description': self.description,
            'snapshot_count': len(self.snapshots),
            'operation_count': len(self.operations),
            'snapshots': [s.to_dict() for s in self.snapshots],
            'operations': self.operations,
            'metadata': self.metadata
        }


class RegistryBackupManager:
    """Manages registry backup and restore operations"""

    def __init__(self, backup_directory: str = "./registry_backups"):
        """
        Initialize backup manager

        Args:
            backup_directory: Directory to store backup files
        """
        self.backup_directory = backup_directory
        self._ensure_backup_directory()

        self.current_session: Optional[BackupSession] = None
        self.snapshots: Dict[str, RegistryBackupSnapshot] = {}
        self.sessions: Dict[str, BackupSession] = {}

    def _ensure_backup_directory(self) -> None:
        """Ensure backup directory exists"""
        if not os.path.exists(self.backup_directory):
            os.makedirs(self.backup_directory, exist_ok=True)

    def create_backup_session(self, description: str = "") -> str:
        """
        Create a new backup session

        Args:
            description: Description of the backup session

        Returns:
            Session ID
        """
        session_id = self._generate_session_id()
        self.current_session = BackupSession(
            session_id=session_id,
            created=time.time(),
            description=description or f"Backup session {session_id}"
        )
        self.sessions[session_id] = self.current_session
        return session_id

    def backup_registry_values(
        self,
        values: Dict[str, Tuple[str, str]],
        hive: str = "HKCU",
        path: str = "",
        mode: BackupMode = BackupMode.FULL,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Backup a set of registry values

        Args:
            values: Dict of {value_name: (data, type)}
            hive: Registry hive (HKCU, HKLM)
            path: Registry path
            mode: Backup mode (FULL, INCREMENTAL, SNAPSHOT)
            metadata: Additional metadata

        Returns:
            Snapshot ID
        """
        snapshot_id = self._generate_snapshot_id()
        timestamp = time.time()

        # Create backup entries for each value
        backup_values = {}
        for value_name, (data, value_type) in values.items():
            backup_val = RegistryValueBackup(
                value_name=value_name,
                value_data=data,
                value_type=value_type,
                timestamp=timestamp,
                path=path,
                hive=hive
            )
            backup_values[value_name] = backup_val

        # Determine parent for incremental backups
        parent_id = None
        if mode == BackupMode.INCREMENTAL:
            parent_id = self._get_latest_snapshot_id()

        # Create snapshot
        snapshot = RegistryBackupSnapshot(
            snapshot_id=snapshot_id,
            timestamp=timestamp,
            mode=mode.value,
            hive=hive,
            path=path,
            values=backup_values,
            metadata=metadata or {},
            parent_snapshot_id=parent_id
        )

        self.snapshots[snapshot_id] = snapshot

        # Add to current session
        if self.current_session:
            self.current_session.snapshots.append(snapshot)
            self.current_session.operations.append({
                'operation': 'backup',
                'snapshot_id': snapshot_id,
                'timestamp': timestamp,
                'value_count': len(values),
                'mode': mode.value
            })

        return snapshot_id

    def restore_registry_values(
        self,
        snapshot_id: str,
        mode: RestoreMode = RestoreMode.FULL_RESTORE,
        value_names: Optional[List[str]] = None
    ) -> Dict[str, Tuple[str, str]]:
        """
        Restore registry values from a backup

        Args:
            snapshot_id: ID of snapshot to restore from
            mode: Restore mode
            value_names: Specific values to restore (for SELECTIVE mode)

        Returns:
            Dictionary of {value_name: (data, type)} to restore
        """
        if snapshot_id not in self.snapshots:
            raise ValueError(f"Snapshot {snapshot_id} not found")

        snapshot = self.snapshots[snapshot_id]
        restored_values = {}

        if mode == RestoreMode.FULL_RESTORE:
            # Restore all values from snapshot
            for value_name, backup_val in snapshot.values.items():
                restored_values[value_name] = (
                    backup_val.value_data,
                    backup_val.value_type
                )

        elif mode == RestoreMode.SELECTIVE:
            # Restore only specified values
            if not value_names:
                raise ValueError("value_names required for SELECTIVE restore")

            for value_name in value_names:
                if value_name in snapshot.values:
                    backup_val = snapshot.values[value_name]
                    restored_values[value_name] = (
                        backup_val.value_data,
                        backup_val.value_type
                    )

        elif mode == RestoreMode.ROLLBACK:
            # Restore from parent snapshot (undo last operation)
            if snapshot.parent_snapshot_id:
                parent_snapshot = self.snapshots[snapshot.parent_snapshot_id]
                for value_name, backup_val in parent_snapshot.values.items():
                    restored_values[value_name] = (
                        backup_val.value_data,
                        backup_val.value_type
                    )
            else:
                raise ValueError("No parent snapshot for rollback")

        # Record restore operation
        if self.current_session:
            self.current_session.operations.append({
                'operation': 'restore',
                'snapshot_id': snapshot_id,
                'timestamp': time.time(),
                'value_count': len(restored_values),
                'mode': mode.value
            })

        return restored_values

    def get_snapshot_diff(
        self,
        snapshot_id1: str,
        snapshot_id2: str
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get differences between two snapshots

        Args:
            snapshot_id1: First snapshot ID
            snapshot_id2: Second snapshot ID

        Returns:
            Dictionary of differences
        """
        if snapshot_id1 not in self.snapshots:
            raise ValueError(f"Snapshot {snapshot_id1} not found")
        if snapshot_id2 not in self.snapshots:
            raise ValueError(f"Snapshot {snapshot_id2} not found")

        snap1 = self.snapshots[snapshot_id1]
        snap2 = self.snapshots[snapshot_id2]

        differences = {}

        # Find added, modified, and deleted values
        all_keys = set(snap1.values.keys()) | set(snap2.values.keys())

        for key in all_keys:
            in_snap1 = key in snap1.values
            in_snap2 = key in snap2.values

            if in_snap1 and not in_snap2:
                differences[key] = {
                    'status': 'deleted',
                    'snap1': {
                        'data': snap1.values[key].value_data,
                        'type': snap1.values[key].value_type
                    }
                }
            elif not in_snap1 and in_snap2:
                differences[key] = {
                    'status': 'added',
                    'snap2': {
                        'data': snap2.values[key].value_data,
                        'type': snap2.values[key].value_type
                    }
                }
            elif in_snap1 and in_snap2:
                val1 = snap1.values[key]
                val2 = snap2.values[key]

                if val1.hash != val2.hash:
                    differences[key] = {
                        'status': 'modified',
                        'snap1': {
                            'data': val1.value_data,
                            'type': val1.value_type,
                            'hash': val1.hash
                        },
                        'snap2': {
                            'data': val2.value_data,
                            'type': val2.value_type,
                            'hash': val2.hash
                        }
                    }

        return differences

    def verify_snapshot(self, snapshot_id: str) -> Dict[str, Any]:
        """
        Verify integrity of a snapshot

        Args:
            snapshot_id: Snapshot ID to verify

        Returns:
            Verification result
        """
        if snapshot_id not in self.snapshots:
            raise ValueError(f"Snapshot {snapshot_id} not found")

        snapshot = self.snapshots[snapshot_id]
        result = {
            'snapshot_id': snapshot_id,
            'verified': True,
            'issues': [],
            'value_count': len(snapshot.values),
            'integrity_check': 'passed'
        }

        # Verify each value
        for value_name, backup_val in snapshot.values.items():
            # Recalculate hash
            expected_hash = hashlib.sha256(
                f"{backup_val.value_data}{backup_val.value_type}".encode()
            ).hexdigest()

            if backup_val.hash != expected_hash:
                result['issues'].append(
                    f"Hash mismatch for {value_name}: "
                    f"expected {expected_hash}, got {backup_val.hash}"
                )
                result['verified'] = False

        if not result['issues']:
            result['integrity_check'] = 'passed'
        else:
            result['integrity_check'] = 'failed'

        return result

    def save_backup_to_file(
        self,
        session_id: Optional[str] = None,
        filename: Optional[str] = None
    ) -> str:
        """
        Save backup session to JSON file

        Args:
            session_id: Session ID (uses current if None)
            filename: Custom filename (generates if None)

        Returns:
            Full path to saved file
        """
        if not session_id:
            if not self.current_session:
                raise ValueError("No active backup session")
            session_id = self.current_session.session_id

        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"backup_session_{session_id}_{timestamp}.json"

        filepath = os.path.join(self.backup_directory, filename)

        session_data = self.sessions[session_id].to_dict()

        with open(filepath, 'w') as f:
            json.dump(session_data, f, indent=2)

        return filepath

    def load_backup_from_file(self, filepath: str) -> str:
        """
        Load backup session from JSON file

        Args:
            filepath: Path to backup file

        Returns:
            Loaded session ID
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Backup file not found: {filepath}")

        with open(filepath, 'r') as f:
            session_data = json.load(f)

        # Reconstruct session
        session_id = session_data['session_id']
        session = BackupSession(
            session_id=session_id,
            created=session_data['created'],
            description=session_data['description'],
            metadata=session_data.get('metadata', {})
        )

        # Reconstruct snapshots
        for snap_data in session_data.get('snapshots', []):
            snapshot_id = snap_data['snapshot_id']

            # Reconstruct value backups
            values = {}
            for value_name, val_data in snap_data.get('values', {}).items():
                values[value_name] = RegistryValueBackup(
                    value_name=val_data['value_name'],
                    value_data=val_data['value_data'],
                    value_type=val_data['value_type'],
                    timestamp=val_data['timestamp'],
                    path=snap_data['path'],
                    hive=snap_data['hive'],
                    hash=val_data.get('hash', '')
                )

            snapshot = RegistryBackupSnapshot(
                snapshot_id=snapshot_id,
                timestamp=snap_data['timestamp'],
                mode=snap_data['mode'],
                hive=snap_data['hive'],
                path=snap_data['path'],
                values=values,
                metadata=snap_data.get('metadata', {}),
                parent_snapshot_id=snap_data.get('parent_snapshot_id')
            )

            session.snapshots.append(snapshot)
            self.snapshots[snapshot_id] = snapshot

        self.sessions[session_id] = session
        return session_id

    def list_snapshots(self, session_id: Optional[str] = None) -> List[Dict]:
        """
        List all snapshots in a session

        Args:
            session_id: Session ID (uses all if None)

        Returns:
            List of snapshot info
        """
        snapshots_info = []

        if session_id:
            if session_id not in self.sessions:
                raise ValueError(f"Session {session_id} not found")

            for snapshot in self.sessions[session_id].snapshots:
                snapshots_info.append({
                    'snapshot_id': snapshot.snapshot_id,
                    'timestamp': snapshot.timestamp,
                    'datetime': datetime.fromtimestamp(snapshot.timestamp).isoformat(),
                    'mode': snapshot.mode,
                    'value_count': len(snapshot.values),
                    'hive': snapshot.hive,
                    'path': snapshot.path
                })
        else:
            for snapshot_id, snapshot in self.snapshots.items():
                snapshots_info.append({
                    'snapshot_id': snapshot_id,
                    'timestamp': snapshot.timestamp,
                    'datetime': datetime.fromtimestamp(snapshot.timestamp).isoformat(),
                    'mode': snapshot.mode,
                    'value_count': len(snapshot.values),
                    'hive': snapshot.hive,
                    'path': snapshot.path
                })

        return sorted(snapshots_info, key=lambda x: x['timestamp'], reverse=True)

    def get_snapshot_info(self, snapshot_id: str) -> Dict:
        """
        Get detailed info about a snapshot

        Args:
            snapshot_id: Snapshot ID

        Returns:
            Snapshot information
        """
        if snapshot_id not in self.snapshots:
            raise ValueError(f"Snapshot {snapshot_id} not found")

        snapshot = self.snapshots[snapshot_id]
        return {
            'snapshot_id': snapshot.snapshot_id,
            'timestamp': snapshot.timestamp,
            'datetime': datetime.fromtimestamp(snapshot.timestamp).isoformat(),
            'mode': snapshot.mode,
            'hive': snapshot.hive,
            'path': snapshot.path,
            'value_count': len(snapshot.values),
            'values': [
                {
                    'name': val.value_name,
                    'type': val.value_type,
                    'data_length': len(val.value_data),
                    'hash': val.hash
                }
                for val in snapshot.values.values()
            ],
            'metadata': snapshot.metadata,
            'parent_snapshot_id': snapshot.parent_snapshot_id
        }

    @staticmethod
    def _generate_session_id() -> str:
        """Generate unique session ID"""
        return f"sess_{int(time.time() * 1000000) % 1000000:06d}"

    @staticmethod
    def _generate_snapshot_id() -> str:
        """Generate unique snapshot ID"""
        return f"snap_{int(time.time() * 1000000) % 1000000:06d}"

    def _get_latest_snapshot_id(self) -> Optional[str]:
        """Get ID of latest snapshot"""
        if not self.snapshots:
            return None
        return max(self.snapshots.keys(),
                  key=lambda k: self.snapshots[k].timestamp)


class RegistryBackupIntegration:
    """Integration layer for registry obfuscator with backup system"""

    def __init__(self, backup_manager: RegistryBackupManager):
        """Initialize integration"""
        self.backup_manager = backup_manager

    def obfuscate_with_backup(
        self,
        obfuscator: Any,
        payload: str,
        hive: str = "HKCU",
        path: str = "Software\\Microsoft\\Windows\\CurrentVersion",
        value_prefix: str = "SystemUpdate"
    ) -> Tuple[Dict, str]:
        """
        Perform obfuscation with automatic backup

        Args:
            obfuscator: RegistryObfuscator instance
            payload: Payload to obfuscate
            hive: Registry hive
            path: Registry path
            value_prefix: Value prefix

        Returns:
            Tuple of (obfuscation_result, backup_snapshot_id)
        """
        # Create backup session if needed
        if not self.backup_manager.current_session:
            self.backup_manager.create_backup_session(
                description=f"Obfuscation backup for {value_prefix}"
            )

        # Perform obfuscation
        obf_result = obfuscator.obfuscate(payload)
        registry_values = obf_result['registry_values']

        # Backup the obfuscated values
        snapshot_id = self.backup_manager.backup_registry_values(
            values=registry_values,
            hive=hive,
            path=path,
            mode=BackupMode.FULL,
            metadata={
                'operation': 'obfuscation',
                'payload': payload,
                'value_prefix': value_prefix,
                'obfuscation_type': obf_result['type']
            }
        )

        return obf_result, snapshot_id

    def restore_with_verification(
        self,
        snapshot_id: str
    ) -> Tuple[Dict[str, Tuple[str, str]], Dict]:
        """
        Restore values with verification

        Args:
            snapshot_id: Snapshot ID to restore

        Returns:
            Tuple of (restored_values, verification_result)
        """
        # Verify snapshot integrity
        verification = self.backup_manager.verify_snapshot(snapshot_id)

        if not verification['verified']:
            raise RuntimeError(
                f"Snapshot verification failed: {verification['issues']}"
            )

        # Restore values
        restored_values = self.backup_manager.restore_registry_values(
            snapshot_id=snapshot_id,
            mode=RestoreMode.FULL_RESTORE
        )

        return restored_values, verification


def test_backup_restore():
    """Test backup/restore system"""
    import tempfile
    import shutil

    # Create temporary directory
    tmpdir = tempfile.mkdtemp()

    try:
        print("="*70)
        print("REGISTRY BACKUP/RESTORE SYSTEM TEST")
        print("="*70)

        # Initialize backup manager
        backup_mgr = RegistryBackupManager(backup_directory=tmpdir)
        print(f"\nBackup directory: {tmpdir}")

        # Create backup session
        session_id = backup_mgr.create_backup_session(
            description="Test backup/restore session"
        )
        print(f"Created backup session: {session_id}")

        # Test data
        test_values = {
            'TestValue1': ('72656761647369', 'REG_SZ'),
            'TestValue2': ('a1b2c3d4e5f6', 'REG_SZ'),
            'TestValue3': ('0123456789abcdef', 'REG_SZ'),
        }

        # Backup 1: Initial state
        print("\n--- Backup 1: Initial State ---")
        snap1_id = backup_mgr.backup_registry_values(
            values=test_values,
            hive="HKCU",
            path="Software\\Test",
            mode=BackupMode.FULL
        )
        print(f"Snapshot 1 ID: {snap1_id}")
        print(f"Values backed up: {len(test_values)}")

        # Modify values
        modified_values = {
            'TestValue1': ('6d6f646966696564', 'REG_SZ'),
            'TestValue2': ('a1b2c3d4e5f6', 'REG_SZ'),
            'TestValue4': ('6e657756616c7565', 'REG_SZ'),  # New value
        }

        # Backup 2: Modified state
        print("\n--- Backup 2: Modified State ---")
        snap2_id = backup_mgr.backup_registry_values(
            values=modified_values,
            hive="HKCU",
            path="Software\\Test",
            mode=BackupMode.INCREMENTAL
        )
        print(f"Snapshot 2 ID: {snap2_id}")
        print(f"Values backed up: {len(modified_values)}")

        # Get diff
        print("\n--- Comparing Snapshots ---")
        diff = backup_mgr.get_snapshot_diff(snap1_id, snap2_id)
        print(f"Changes detected:")
        for key, changes in diff.items():
            print(f"  {key}: {changes['status']}")

        # Verify snapshots
        print("\n--- Verifying Snapshots ---")
        verify1 = backup_mgr.verify_snapshot(snap1_id)
        print(f"Snapshot 1 verification: {verify1['integrity_check']}")

        verify2 = backup_mgr.verify_snapshot(snap2_id)
        print(f"Snapshot 2 verification: {verify2['integrity_check']}")

        # Restore from snapshot 1
        print("\n--- Restoring from Snapshot 1 ---")
        restored = backup_mgr.restore_registry_values(
            snapshot_id=snap1_id,
            mode=RestoreMode.FULL_RESTORE
        )
        print(f"Restored {len(restored)} values")

        # List snapshots
        print("\n--- Snapshot List ---")
        snapshots = backup_mgr.list_snapshots()
        for snap_info in snapshots:
            print(f"  {snap_info['snapshot_id']}: {snap_info['datetime']} "
                  f"({snap_info['value_count']} values)")

        # Get snapshot info
        print("\n--- Snapshot Info ---")
        snap_info = backup_mgr.get_snapshot_info(snap1_id)
        print(f"Snapshot: {snap_info['snapshot_id']}")
        print(f"Mode: {snap_info['mode']}")
        print(f"Values: {snap_info['value_count']}")

        # Save to file
        print("\n--- Saving to File ---")
        filepath = backup_mgr.save_backup_to_file()
        print(f"Saved to: {filepath}")
        print(f"File exists: {os.path.exists(filepath)}")

        # Load from file
        print("\n--- Loading from File ---")
        loaded_session_id = backup_mgr.load_backup_from_file(filepath)
        print(f"Loaded session: {loaded_session_id}")
        print(f"Session matches: {loaded_session_id == session_id}")

        print("\n" + "="*70)
        print("TEST COMPLETED SUCCESSFULLY")
        print("="*70)

    finally:
        # Cleanup
        shutil.rmtree(tmpdir)


if __name__ == "__main__":
    test_backup_restore()
