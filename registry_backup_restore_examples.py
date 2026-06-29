#!/usr/bin/env python3
"""
Registry Backup/Restore System - Practical Examples
Demonstrates common usage patterns and integration scenarios
"""

import json
from registry_backup_restore import (
    RegistryBackupManager,
    RegistryBackupIntegration,
    BackupMode,
    RestoreMode
)


def example_1_basic_backup_restore():
    """Example 1: Basic Backup and Restore"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Backup and Restore")
    print("="*70)

    # Initialize backup manager
    backup_mgr = RegistryBackupManager()

    # Create backup session
    session_id = backup_mgr.create_backup_session(
        description="Basic backup example"
    )
    print(f"Created session: {session_id}")

    # Define registry values to backup
    registry_values = {
        'SystemUpdate_PayloadData': ('48656c6c6f20576f726c64', 'REG_SZ'),
        'SystemUpdate_Offset': ('0', 'REG_SZ'),
        'SystemUpdate_Size': ('11', 'REG_SZ'),
    }

    # Backup the values
    snapshot_id = backup_mgr.backup_registry_values(
        values=registry_values,
        hive="HKCU",
        path="Software\\Microsoft\\Windows\\CurrentVersion"
    )
    print(f"Backed up snapshot: {snapshot_id}")

    # Restore the values
    restored_values = backup_mgr.restore_registry_values(
        snapshot_id=snapshot_id,
        mode=RestoreMode.FULL_RESTORE
    )

    print(f"Restored {len(restored_values)} values:")
    for name, (data, reg_type) in restored_values.items():
        print(f"  {name}: {data[:30]}... ({reg_type})")


def example_2_incremental_backup():
    """Example 2: Incremental Backup with Parent Tracking"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Incremental Backup with Parent Tracking")
    print("="*70)

    backup_mgr = RegistryBackupManager()
    session_id = backup_mgr.create_backup_session(
        description="Incremental backup example"
    )

    # Initial full backup
    initial_values = {
        'Value1': ('data1', 'REG_SZ'),
        'Value2': ('data2', 'REG_SZ'),
    }
    snap1_id = backup_mgr.backup_registry_values(
        values=initial_values,
        mode=BackupMode.FULL
    )
    print(f"Initial snapshot: {snap1_id}")

    # Incremental backup 1
    modified_values = {
        'Value1': ('modified1', 'REG_SZ'),  # Modified
        'Value3': ('data3', 'REG_SZ'),      # New
    }
    snap2_id = backup_mgr.backup_registry_values(
        values=modified_values,
        mode=BackupMode.INCREMENTAL
    )
    print(f"Incremental snapshot 1: {snap2_id}")

    # Incremental backup 2
    more_changes = {
        'Value4': ('data4', 'REG_SZ'),
    }
    snap3_id = backup_mgr.backup_registry_values(
        values=more_changes,
        mode=BackupMode.INCREMENTAL
    )
    print(f"Incremental snapshot 2: {snap3_id}")

    # Show parent relationships
    snap2 = backup_mgr.snapshots[snap2_id]
    snap3 = backup_mgr.snapshots[snap3_id]
    print(f"\nSnapshot chain:")
    print(f"  {snap1_id} (initial)")
    print(f"  {snap2_id} <- parent: {snap2.parent_snapshot_id}")
    print(f"  {snap3_id} <- parent: {snap3.parent_snapshot_id}")


def example_3_snapshot_diffing():
    """Example 3: Comparing Snapshots with Diffing"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Snapshot Diffing")
    print("="*70)

    backup_mgr = RegistryBackupManager()
    backup_mgr.create_backup_session("Snapshot diffing example")

    # Create first snapshot
    values1 = {
        'Name': ('Alice', 'REG_SZ'),
        'Age': ('30', 'REG_DWORD'),
        'Email': ('alice@example.com', 'REG_SZ'),
    }
    snap1_id = backup_mgr.backup_registry_values(values=values1)
    print(f"Snapshot 1: {snap1_id}")
    print("  Values: Name, Age, Email")

    # Create second snapshot with changes
    values2 = {
        'Name': ('Alice Johnson', 'REG_SZ'),  # Modified
        'Age': ('30', 'REG_DWORD'),           # Unchanged
        'Phone': ('555-1234', 'REG_SZ'),      # Added
        # Email deleted
    }
    snap2_id = backup_mgr.backup_registry_values(values=values2)
    print(f"Snapshot 2: {snap2_id}")
    print("  Values: Name, Age, Phone")

    # Get differences
    diff = backup_mgr.get_snapshot_diff(snap1_id, snap2_id)
    print(f"\nChanges between snapshots:")
    print(f"{'Value':<15} {'Status':<12} {'Details'}")
    print("-" * 50)

    for key, change in diff.items():
        status = change['status']
        if status == 'modified':
            old_data = change['snap1']['data']
            new_data = change['snap2']['data']
            print(f"{key:<15} {status:<12} '{old_data}' -> '{new_data}'")
        elif status == 'added':
            new_data = change['snap2']['data']
            print(f"{key:<15} {status:<12} (added: '{new_data}')")
        elif status == 'deleted':
            old_data = change['snap1']['data']
            print(f"{key:<15} {status:<12} (was: '{old_data}')")


def example_4_selective_restore():
    """Example 4: Selective Value Restore"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Selective Restore")
    print("="*70)

    backup_mgr = RegistryBackupManager()
    backup_mgr.create_backup_session("Selective restore example")

    # Create backup
    values = {
        'Database_Host': ('localhost', 'REG_SZ'),
        'Database_Port': ('5432', 'REG_DWORD'),
        'Database_User': ('admin', 'REG_SZ'),
        'Database_Pass': ('secret', 'REG_SZ'),
        'API_Key': ('key123456', 'REG_SZ'),
    }
    snapshot_id = backup_mgr.backup_registry_values(values=values)
    print(f"Created snapshot with {len(values)} values: {snapshot_id}")

    # Selectively restore only database settings
    restored = backup_mgr.restore_registry_values(
        snapshot_id=snapshot_id,
        mode=RestoreMode.SELECTIVE,
        value_names=['Database_Host', 'Database_Port', 'Database_User']
    )

    print(f"\nSelectively restored {len(restored)} database values:")
    for name, (data, reg_type) in restored.items():
        print(f"  {name}: {data} ({reg_type})")

    print(f"\nNote: API_Key was NOT restored (selective restore)")


def example_5_verification():
    """Example 5: Snapshot Verification"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Snapshot Verification")
    print("="*70)

    backup_mgr = RegistryBackupManager()
    backup_mgr.create_backup_session("Verification example")

    # Create snapshot
    values = {
        'Config1': ('value1', 'REG_SZ'),
        'Config2': ('value2', 'REG_SZ'),
        'Config3': ('value3', 'REG_SZ'),
    }
    snapshot_id = backup_mgr.backup_registry_values(values=values)

    # Verify integrity
    verification = backup_mgr.verify_snapshot(snapshot_id)

    print(f"Verification Results:")
    print(f"  Snapshot ID: {verification['snapshot_id']}")
    print(f"  Verified: {verification['verified']}")
    print(f"  Integrity Check: {verification['integrity_check']}")
    print(f"  Value Count: {verification['value_count']}")

    if verification['issues']:
        print(f"  Issues Found:")
        for issue in verification['issues']:
            print(f"    - {issue}")
    else:
        print(f"  No issues detected - snapshot is intact")


def example_6_snapshot_info():
    """Example 6: Getting Snapshot Information"""
    print("\n" + "="*70)
    print("EXAMPLE 6: Snapshot Information")
    print("="*70)

    backup_mgr = RegistryBackupManager()
    backup_mgr.create_backup_session("Snapshot info example")

    # Create snapshot with metadata
    values = {
        'Setting1': ('value1', 'REG_SZ'),
        'Setting2': ('value2', 'REG_DWORD'),
    }
    snapshot_id = backup_mgr.backup_registry_values(
        values=values,
        hive="HKCU",
        path="Software\\MyApp\\Settings",
        metadata={
            'operation': 'configuration_backup',
            'version': '2.0',
            'operator': 'automation'
        }
    )

    # Get detailed info
    info = backup_mgr.get_snapshot_info(snapshot_id)

    print(f"Snapshot Details:")
    print(f"  ID: {info['snapshot_id']}")
    print(f"  DateTime: {info['datetime']}")
    print(f"  Mode: {info['mode']}")
    print(f"  Hive: {info['hive']}")
    print(f"  Path: {info['path']}")
    print(f"  Value Count: {info['value_count']}")
    print(f"\nMetadata:")
    for key, value in info['metadata'].items():
        print(f"  {key}: {value}")
    print(f"\nValues:")
    for value in info['values']:
        print(f"  {value['name']}: {value['data_length']} bytes ({value['type']})")


def example_7_listing_snapshots():
    """Example 7: Listing All Snapshots"""
    print("\n" + "="*70)
    print("EXAMPLE 7: Listing Snapshots")
    print("="*70)

    backup_mgr = RegistryBackupManager()
    backup_mgr.create_backup_session("Snapshot listing example")

    # Create multiple snapshots
    for i in range(3):
        values = {f'Value{i}': (f'data{i}', 'REG_SZ')}
        backup_mgr.backup_registry_values(values=values)

    # List all snapshots
    snapshots = backup_mgr.list_snapshots()

    print(f"Total Snapshots: {len(snapshots)}\n")
    print(f"{'ID':<20} {'DateTime':<25} {'Mode':<12} {'Values':<10}")
    print("-" * 70)

    for snap in snapshots:
        print(f"{snap['snapshot_id']:<20} {snap['datetime']:<25} "
              f"{snap['mode']:<12} {snap['value_count']:<10}")


def example_8_file_persistence():
    """Example 8: Save and Load Backups"""
    print("\n" + "="*70)
    print("EXAMPLE 8: File Persistence")
    print("="*70)

    # Create and save backup
    backup_mgr = RegistryBackupManager()
    session_id = backup_mgr.create_backup_session(
        description="File persistence example"
    )

    values = {
        'Config1': ('value1', 'REG_SZ'),
        'Config2': ('value2', 'REG_SZ'),
    }
    backup_mgr.backup_registry_values(values=values)

    # Save to file
    filepath = backup_mgr.save_backup_to_file()
    print(f"Saved backup to: {filepath}")

    # Show file content (first 500 chars)
    with open(filepath, 'r') as f:
        content = f.read()
        print(f"File size: {len(content)} bytes")
        print(f"First 300 chars of JSON:")
        print(content[:300] + "...")

    # Load into new manager
    new_mgr = RegistryBackupManager()
    loaded_session_id = new_mgr.load_backup_from_file(filepath)

    print(f"\nLoaded session: {loaded_session_id}")
    print(f"Sessions match: {loaded_session_id == session_id}")

    # Verify we can restore from loaded backup
    snapshots = new_mgr.list_snapshots()
    if snapshots:
        snapshot_id = snapshots[0]['snapshot_id']
        restored = new_mgr.restore_registry_values(
            snapshot_id=snapshot_id
        )
        print(f"Successfully restored {len(restored)} values from loaded backup")


def example_9_rollback():
    """Example 9: Rollback to Previous State"""
    print("\n" + "="*70)
    print("EXAMPLE 9: Rollback Functionality")
    print("="*70)

    backup_mgr = RegistryBackupManager()
    backup_mgr.create_backup_session("Rollback example")

    # Step 1: Initial state
    print("Step 1: Initial Configuration")
    initial = {'Setting': ('original', 'REG_SZ')}
    snap1 = backup_mgr.backup_registry_values(
        values=initial,
        mode=BackupMode.FULL
    )
    print(f"  Snapshot: {snap1}")
    print(f"  Setting: {initial['Setting'][0]}")

    # Step 2: First modification
    print("\nStep 2: First Modification")
    modified1 = {'Setting': ('modified_once', 'REG_SZ')}
    snap2 = backup_mgr.backup_registry_values(
        values=modified1,
        mode=BackupMode.INCREMENTAL
    )
    print(f"  Snapshot: {snap2}")
    print(f"  Setting: {modified1['Setting'][0]}")

    # Step 3: Second modification
    print("\nStep 3: Second Modification")
    modified2 = {'Setting': ('modified_twice', 'REG_SZ')}
    snap3 = backup_mgr.backup_registry_values(
        values=modified2,
        mode=BackupMode.INCREMENTAL
    )
    print(f"  Snapshot: {snap3}")
    print(f"  Setting: {modified2['Setting'][0]}")

    # Step 4: Error detected, rollback to previous
    print("\nStep 4: Error Detected - Rolling Back")
    restored = backup_mgr.restore_registry_values(
        snapshot_id=snap3,
        mode=RestoreMode.ROLLBACK
    )
    print(f"  Rolled back from {snap3} to parent")
    print(f"  Restored Setting: {restored['Setting'][0]}")

    # Step 5: Rollback again
    print("\nStep 5: Rollback Again to Initial")
    snap2_obj = backup_mgr.snapshots[snap2]
    restored_again = backup_mgr.restore_registry_values(
        snapshot_id=snap2,
        mode=RestoreMode.ROLLBACK
    )
    print(f"  Rolled back from {snap2} to parent")
    print(f"  Restored Setting: {restored_again['Setting'][0]}")


def example_10_obfuscator_integration():
    """Example 10: Integration with Obfuscator (Simulated)"""
    print("\n" + "="*70)
    print("EXAMPLE 10: Obfuscator Integration")
    print("="*70)

    # Simulate obfuscator
    class MockObfuscator:
        def obfuscate(self, payload):
            return {
                'type': 'binary',
                'registry_values': {
                    'PayloadData': ('68656c6c6f', 'REG_SZ'),
                    'PayloadOffset': ('0', 'REG_SZ'),
                    'PayloadSize': (str(len(payload)), 'REG_SZ'),
                },
                'retrieval_code': 'VBS_CODE_HERE'
            }

    # Initialize
    backup_mgr = RegistryBackupManager()
    integration = RegistryBackupIntegration(backup_mgr)

    # Simulate obfuscation with backup
    obfuscator = MockObfuscator()
    payload = "powershell.exe -Command 'test'"

    result, snapshot_id = integration.obfuscate_with_backup(
        obfuscator=obfuscator,
        payload=payload,
        hive="HKCU",
        path="Software\\Test",
        value_prefix="SystemUpdate"
    )

    print(f"Obfuscation completed:")
    print(f"  Snapshot ID: {snapshot_id}")
    print(f"  Payload: {payload}")
    print(f"  Registry Values: {len(result['registry_values'])}")

    # Restore with verification
    restored, verification = integration.restore_with_verification(
        snapshot_id=snapshot_id
    )

    print(f"\nRestore with Verification:")
    print(f"  Verified: {verification['verified']}")
    print(f"  Integrity: {verification['integrity_check']}")
    print(f"  Restored Values: {len(restored)}")


def main():
    """Run all examples"""
    print("\n" * 2)
    print("REGISTRY BACKUP/RESTORE SYSTEM - PRACTICAL EXAMPLES")
    print("=" * 70)

    examples = [
        example_1_basic_backup_restore,
        example_2_incremental_backup,
        example_3_snapshot_diffing,
        example_4_selective_restore,
        example_5_verification,
        example_6_snapshot_info,
        example_7_listing_snapshots,
        example_8_file_persistence,
        example_9_rollback,
        example_10_obfuscator_integration,
    ]

    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"Error in {example.__name__}: {e}")

    print("\n" + "=" * 70)
    print("ALL EXAMPLES COMPLETED")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
