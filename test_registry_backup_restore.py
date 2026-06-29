#!/usr/bin/env python3
"""
Comprehensive test suite for Registry Backup/Restore System
Tests all backup, restore, verification, and integration functionality
"""

import unittest
import tempfile
import shutil
import os
import json
import time
from datetime import datetime
from registry_backup_restore import (
    RegistryBackupManager,
    RegistryBackupIntegration,
    BackupMode,
    RestoreMode,
    RegistryValueBackup,
    RegistryBackupSnapshot,
    BackupSession
)


class TestRegistryValueBackup(unittest.TestCase):
    """Test RegistryValueBackup data class"""

    def test_value_backup_creation(self):
        """Test creating a value backup"""
        backup = RegistryValueBackup(
            value_name="TestValue",
            value_data="74657374646174610a",
            value_type="REG_SZ",
            timestamp=time.time(),
            path="Software\\Test",
            hive="HKCU"
        )
        self.assertEqual(backup.value_name, "TestValue")
        self.assertEqual(backup.value_type, "REG_SZ")
        self.assertIsNotNone(backup.hash)

    def test_value_backup_hash_generation(self):
        """Test hash generation for value backup"""
        backup1 = RegistryValueBackup(
            value_name="TestValue",
            value_data="testdata",
            value_type="REG_SZ",
            timestamp=time.time(),
            path="Software\\Test",
            hive="HKCU"
        )

        backup2 = RegistryValueBackup(
            value_name="TestValue",
            value_data="testdata",
            value_type="REG_SZ",
            timestamp=time.time(),
            path="Software\\Test",
            hive="HKCU"
        )

        self.assertEqual(backup1.hash, backup2.hash)

    def test_value_backup_hash_differs_on_change(self):
        """Test that hash changes when data changes"""
        backup1 = RegistryValueBackup(
            value_name="TestValue",
            value_data="testdata1",
            value_type="REG_SZ",
            timestamp=time.time(),
            path="Software\\Test",
            hive="HKCU"
        )

        backup2 = RegistryValueBackup(
            value_name="TestValue",
            value_data="testdata2",
            value_type="REG_SZ",
            timestamp=time.time(),
            path="Software\\Test",
            hive="HKCU"
        )

        self.assertNotEqual(backup1.hash, backup2.hash)


class TestBackupManager(unittest.TestCase):
    """Test RegistryBackupManager class"""

    def setUp(self):
        """Set up test fixtures"""
        self.tmpdir = tempfile.mkdtemp()
        self.backup_mgr = RegistryBackupManager(backup_directory=self.tmpdir)

    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.tmpdir)

    def test_backup_directory_creation(self):
        """Test backup directory is created"""
        self.assertTrue(os.path.exists(self.tmpdir))

    def test_create_backup_session(self):
        """Test creating a backup session"""
        session_id = self.backup_mgr.create_backup_session(
            description="Test session"
        )
        self.assertIsNotNone(session_id)
        self.assertIn(session_id, self.backup_mgr.sessions)

    def test_backup_registry_values_full(self):
        """Test full backup of registry values"""
        session_id = self.backup_mgr.create_backup_session()

        test_values = {
            'Value1': ('data1', 'REG_SZ'),
            'Value2': ('data2', 'REG_DWORD'),
        }

        snapshot_id = self.backup_mgr.backup_registry_values(
            values=test_values,
            hive="HKCU",
            path="Software\\Test",
            mode=BackupMode.FULL
        )

        self.assertIsNotNone(snapshot_id)
        self.assertIn(snapshot_id, self.backup_mgr.snapshots)

        snapshot = self.backup_mgr.snapshots[snapshot_id]
        self.assertEqual(len(snapshot.values), 2)
        self.assertEqual(snapshot.mode, "full")

    def test_backup_registry_values_incremental(self):
        """Test incremental backup"""
        session_id = self.backup_mgr.create_backup_session()

        # First backup
        values1 = {'Value1': ('data1', 'REG_SZ')}
        snap1_id = self.backup_mgr.backup_registry_values(
            values=values1,
            mode=BackupMode.FULL
        )

        # Second backup (incremental)
        values2 = {'Value2': ('data2', 'REG_SZ')}
        snap2_id = self.backup_mgr.backup_registry_values(
            values=values2,
            mode=BackupMode.INCREMENTAL
        )

        snap2 = self.backup_mgr.snapshots[snap2_id]
        self.assertEqual(snap2.parent_snapshot_id, snap1_id)

    def test_restore_full(self):
        """Test full restore from snapshot"""
        session_id = self.backup_mgr.create_backup_session()

        test_values = {
            'Value1': ('data1', 'REG_SZ'),
            'Value2': ('data2', 'REG_DWORD'),
        }

        snapshot_id = self.backup_mgr.backup_registry_values(
            values=test_values
        )

        restored = self.backup_mgr.restore_registry_values(
            snapshot_id=snapshot_id,
            mode=RestoreMode.FULL_RESTORE
        )

        self.assertEqual(len(restored), 2)
        self.assertEqual(restored['Value1'], ('data1', 'REG_SZ'))
        self.assertEqual(restored['Value2'], ('data2', 'REG_DWORD'))

    def test_restore_selective(self):
        """Test selective restore from snapshot"""
        session_id = self.backup_mgr.create_backup_session()

        test_values = {
            'Value1': ('data1', 'REG_SZ'),
            'Value2': ('data2', 'REG_DWORD'),
            'Value3': ('data3', 'REG_SZ'),
        }

        snapshot_id = self.backup_mgr.backup_registry_values(
            values=test_values
        )

        restored = self.backup_mgr.restore_registry_values(
            snapshot_id=snapshot_id,
            mode=RestoreMode.SELECTIVE,
            value_names=['Value1', 'Value3']
        )

        self.assertEqual(len(restored), 2)
        self.assertIn('Value1', restored)
        self.assertIn('Value3', restored)
        self.assertNotIn('Value2', restored)

    def test_restore_rollback(self):
        """Test rollback to parent snapshot"""
        session_id = self.backup_mgr.create_backup_session()

        # First snapshot
        values1 = {'Value1': ('data1', 'REG_SZ')}
        snap1_id = self.backup_mgr.backup_registry_values(
            values=values1,
            mode=BackupMode.FULL
        )

        # Second snapshot (incremental)
        values2 = {'Value2': ('data2', 'REG_SZ')}
        snap2_id = self.backup_mgr.backup_registry_values(
            values=values2,
            mode=BackupMode.INCREMENTAL
        )

        # Rollback to first
        restored = self.backup_mgr.restore_registry_values(
            snapshot_id=snap2_id,
            mode=RestoreMode.ROLLBACK
        )

        self.assertIn('Value1', restored)

    def test_snapshot_diff(self):
        """Test getting differences between snapshots"""
        session_id = self.backup_mgr.create_backup_session()

        # Snapshot 1
        values1 = {
            'Value1': ('data1', 'REG_SZ'),
            'Value2': ('data2', 'REG_SZ'),
        }
        snap1_id = self.backup_mgr.backup_registry_values(values=values1)

        # Snapshot 2
        values2 = {
            'Value1': ('modified1', 'REG_SZ'),  # Modified
            'Value3': ('data3', 'REG_SZ'),      # Added
            # Value2 deleted
        }
        snap2_id = self.backup_mgr.backup_registry_values(values=values2)

        diff = self.backup_mgr.get_snapshot_diff(snap1_id, snap2_id)

        self.assertIn('Value1', diff)
        self.assertEqual(diff['Value1']['status'], 'modified')
        self.assertIn('Value3', diff)
        self.assertEqual(diff['Value3']['status'], 'added')
        self.assertIn('Value2', diff)
        self.assertEqual(diff['Value2']['status'], 'deleted')

    def test_verify_snapshot(self):
        """Test snapshot verification"""
        session_id = self.backup_mgr.create_backup_session()

        test_values = {
            'Value1': ('data1', 'REG_SZ'),
            'Value2': ('data2', 'REG_SZ'),
        }

        snapshot_id = self.backup_mgr.backup_registry_values(
            values=test_values
        )

        verification = self.backup_mgr.verify_snapshot(snapshot_id)

        self.assertTrue(verification['verified'])
        self.assertEqual(verification['integrity_check'], 'passed')
        self.assertEqual(len(verification['issues']), 0)

    def test_list_snapshots(self):
        """Test listing snapshots"""
        session_id = self.backup_mgr.create_backup_session()

        # Create multiple snapshots
        for i in range(3):
            values = {f'Value{i}': (f'data{i}', 'REG_SZ')}
            self.backup_mgr.backup_registry_values(values=values)

        snapshots = self.backup_mgr.list_snapshots()
        self.assertEqual(len(snapshots), 3)

    def test_get_snapshot_info(self):
        """Test getting snapshot information"""
        session_id = self.backup_mgr.create_backup_session()

        test_values = {
            'Value1': ('data1', 'REG_SZ'),
            'Value2': ('data2', 'REG_DWORD'),
        }

        snapshot_id = self.backup_mgr.backup_registry_values(
            values=test_values,
            hive="HKCU",
            path="Software\\Test"
        )

        info = self.backup_mgr.get_snapshot_info(snapshot_id)

        self.assertEqual(info['snapshot_id'], snapshot_id)
        self.assertEqual(info['value_count'], 2)
        self.assertEqual(info['hive'], "HKCU")
        self.assertEqual(info['path'], "Software\\Test")

    def test_save_backup_to_file(self):
        """Test saving backup to file"""
        session_id = self.backup_mgr.create_backup_session(
            description="Test session"
        )

        test_values = {
            'Value1': ('data1', 'REG_SZ'),
        }
        self.backup_mgr.backup_registry_values(values=test_values)

        filepath = self.backup_mgr.save_backup_to_file()

        self.assertTrue(os.path.exists(filepath))
        self.assertTrue(filepath.endswith('.json'))

        # Verify file content
        with open(filepath, 'r') as f:
            data = json.load(f)
            self.assertEqual(data['session_id'], session_id)
            self.assertEqual(data['description'], "Test session")

    def test_load_backup_from_file(self):
        """Test loading backup from file"""
        # Create and save backup
        session_id = self.backup_mgr.create_backup_session(
            description="Test session"
        )

        test_values = {
            'Value1': ('data1', 'REG_SZ'),
            'Value2': ('data2', 'REG_DWORD'),
        }
        snapshot_id = self.backup_mgr.backup_registry_values(
            values=test_values
        )

        filepath = self.backup_mgr.save_backup_to_file()

        # Create new manager and load
        new_mgr = RegistryBackupManager(backup_directory=self.tmpdir)
        loaded_session_id = new_mgr.load_backup_from_file(filepath)

        self.assertEqual(loaded_session_id, session_id)
        self.assertIn(session_id, new_mgr.sessions)
        self.assertIn(snapshot_id, new_mgr.snapshots)

    def test_metadata_preservation(self):
        """Test that metadata is preserved"""
        session_id = self.backup_mgr.create_backup_session()

        test_values = {'Value1': ('data1', 'REG_SZ')}
        metadata = {
            'operation': 'test_operation',
            'custom_field': 'custom_value'
        }

        snapshot_id = self.backup_mgr.backup_registry_values(
            values=test_values,
            metadata=metadata
        )

        snapshot = self.backup_mgr.snapshots[snapshot_id]
        self.assertEqual(snapshot.metadata['operation'], 'test_operation')
        self.assertEqual(snapshot.metadata['custom_field'], 'custom_value')


class TestBackupIntegration(unittest.TestCase):
    """Test integration with registry obfuscator"""

    def setUp(self):
        """Set up test fixtures"""
        self.tmpdir = tempfile.mkdtemp()
        self.backup_mgr = RegistryBackupManager(backup_directory=self.tmpdir)
        self.integration = RegistryBackupIntegration(self.backup_mgr)

    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.tmpdir)

    def test_obfuscate_with_backup(self):
        """Test obfuscation with automatic backup"""
        # Mock obfuscator
        class MockObfuscator:
            def obfuscate(self, payload):
                return {
                    'type': 'test',
                    'registry_values': {
                        'Value1': ('obf_data1', 'REG_SZ'),
                        'Value2': ('obf_data2', 'REG_SZ'),
                    },
                    'retrieval_code': 'mock_code'
                }

        obfuscator = MockObfuscator()

        result, snapshot_id = self.integration.obfuscate_with_backup(
            obfuscator=obfuscator,
            payload="test_payload"
        )

        self.assertIsNotNone(snapshot_id)
        self.assertIn(snapshot_id, self.backup_mgr.snapshots)
        self.assertEqual(result['type'], 'test')

    def test_restore_with_verification(self):
        """Test restore with verification"""
        session_id = self.backup_mgr.create_backup_session()

        test_values = {
            'Value1': ('data1', 'REG_SZ'),
            'Value2': ('data2', 'REG_SZ'),
        }

        snapshot_id = self.backup_mgr.backup_registry_values(
            values=test_values
        )

        restored, verification = self.integration.restore_with_verification(
            snapshot_id=snapshot_id
        )

        self.assertTrue(verification['verified'])
        self.assertEqual(len(restored), 2)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""

    def setUp(self):
        """Set up test fixtures"""
        self.tmpdir = tempfile.mkdtemp()
        self.backup_mgr = RegistryBackupManager(backup_directory=self.tmpdir)

    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.tmpdir)

    def test_restore_nonexistent_snapshot(self):
        """Test restoring from nonexistent snapshot"""
        with self.assertRaises(ValueError):
            self.backup_mgr.restore_registry_values(
                snapshot_id="nonexistent"
            )

    def test_selective_restore_without_value_names(self):
        """Test selective restore without value names"""
        session_id = self.backup_mgr.create_backup_session()
        test_values = {'Value1': ('data1', 'REG_SZ')}
        snapshot_id = self.backup_mgr.backup_registry_values(
            values=test_values
        )

        with self.assertRaises(ValueError):
            self.backup_mgr.restore_registry_values(
                snapshot_id=snapshot_id,
                mode=RestoreMode.SELECTIVE
            )

    def test_empty_backup(self):
        """Test backing up empty values"""
        session_id = self.backup_mgr.create_backup_session()
        snapshot_id = self.backup_mgr.backup_registry_values(values={})

        snapshot = self.backup_mgr.snapshots[snapshot_id]
        self.assertEqual(len(snapshot.values), 0)

    def test_large_value_backup(self):
        """Test backing up large values"""
        session_id = self.backup_mgr.create_backup_session()

        # Create large value
        large_data = 'a' * 10000
        test_values = {'LargeValue': (large_data, 'REG_SZ')}

        snapshot_id = self.backup_mgr.backup_registry_values(
            values=test_values
        )

        restored = self.backup_mgr.restore_registry_values(
            snapshot_id=snapshot_id
        )

        self.assertEqual(len(restored['LargeValue'][0]), 10000)

    def test_special_characters_in_values(self):
        """Test values with special characters"""
        session_id = self.backup_mgr.create_backup_session()

        test_values = {
            'Value1': ('data\\with\\backslashes', 'REG_SZ'),
            'Value2': ('data"with"quotes', 'REG_SZ'),
            'Value3': ('data\nwith\nnewlines', 'REG_SZ'),
        }

        snapshot_id = self.backup_mgr.backup_registry_values(
            values=test_values
        )

        restored = self.backup_mgr.restore_registry_values(
            snapshot_id=snapshot_id
        )

        self.assertEqual(restored['Value1'][0], 'data\\with\\backslashes')
        self.assertEqual(restored['Value2'][0], 'data"with"quotes')
        self.assertEqual(restored['Value3'][0], 'data\nwith\nnewlines')


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestRegistryValueBackup))
    suite.addTests(loader.loadTestsFromTestCase(TestBackupManager))
    suite.addTests(loader.loadTestsFromTestCase(TestBackupIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    import sys
    success = run_tests()
    sys.exit(0 if success else 1)
