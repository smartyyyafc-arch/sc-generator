#!/usr/bin/env python3
"""
COM Polymorphic Loader - Integration Examples
Demonstrates real-world usage scenarios and patterns
"""

from com_polymorphic_loader import (
    COMPolymorphicLoader,
    COMPolymorphicCodeGenerator,
    COMObjectType
)
import json


def example_1_same_code_multiple_objects():
    """
    Example 1: Same code using different COM objects
    Demonstrates the core polymorphism concept
    """
    print("\n" + "=" * 90)
    print("EXAMPLE 1: POLYMORPHISM - SAME CODE, DIFFERENT OBJECTS")
    print("=" * 90 + "\n")

    loader = COMPolymorphicLoader()

    # Define a common operation interface
    def execute_operation(object_type, method, *args):
        """Execute operation using any COM object"""
        return loader.generate_polymorphic_code(
            object_type,
            method,
            *args,
            fallback=False
        )

    # Use the SAME function with DIFFERENT COM objects
    operations = [
        (COMObjectType.SHELL, "Run", "calc.exe", "Execute Shell Command"),
        (COMObjectType.WMI_LOCATOR, "ExecQuery", "SELECT * FROM Win32_Process", "Execute WMI Query"),
        (COMObjectType.EXCEL, "Open", "C:\\file.xlsx", "Open Excel File"),
        (COMObjectType.MSXML, "LoadXML", "<root></root>", "Load XML"),
    ]

    for object_type, method, arg, description in operations:
        print(f"[{description}]")
        print(f"Object Type: {object_type.value}")
        print(f"Method: {method}")
        print("-" * 90)
        code = execute_operation(object_type, method, arg)
        # Print first 200 chars for brevity
        print(code[:200] + "..." if len(code) > 200 else code)
        print()


def example_2_fallback_chain_resilience():
    """
    Example 2: Automatic fallback chains for resilience
    Shows how polymorphic loader improves robustness
    """
    print("\n" + "=" * 90)
    print("EXAMPLE 2: RESILIENCE - FALLBACK CHAINS")
    print("=" * 90 + "\n")

    loader = COMPolymorphicLoader()

    # Primary object might not be available
    print("[Scenario: Primary COM object unavailable]")
    print("Goal: Execute command, but Shell may not be accessible")
    print("-" * 90)

    # Generate code with fallback
    code = loader.generate_polymorphic_code(
        COMObjectType.SHELL,
        "Run",
        "powershell.exe -NoProfile -Command Get-Process",
        fallback=True,
        use_error_handling=True
    )

    print("Generated code will:")
    print("1. Try to create WScript.Shell")
    print("2. If that fails, fallback to WbemScripting.SWbemLocator")
    print("3. Automatically handle errors gracefully")
    print("\nCode snippet:")
    print("-" * 90)
    # Print key parts
    for line in code.split('\n')[:15]:
        print(line)
    print("...")


def example_3_dynamic_object_selection():
    """
    Example 3: Dynamic object selection based on requirements
    Shows flexibility of polymorphic loader
    """
    print("\n" + "=" * 90)
    print("EXAMPLE 3: DYNAMIC SELECTION - CHOOSE RIGHT TOOL FOR JOB")
    print("=" * 90 + "\n")

    loader = COMPolymorphicLoader()

    # Define requirements
    tasks = [
        {
            "name": "List Processes",
            "preferred": COMObjectType.WMI_LOCATOR,
            "alternative": COMObjectType.SHELL,
            "reason": "WMI provides structured data, Shell has fallback"
        },
        {
            "name": "Execute Command",
            "preferred": COMObjectType.SHELL,
            "alternative": COMObjectType.WMI_LOCATOR,
            "reason": "Shell is direct, WMI is fallback"
        },
        {
            "name": "Read Registry",
            "preferred": COMObjectType.SHELL,
            "alternative": None,
            "reason": "Shell is primary method for registry access"
        },
        {
            "name": "Process XML",
            "preferred": COMObjectType.MSXML,
            "alternative": None,
            "reason": "MSXML is specialized for XML"
        },
    ]

    for task in tasks:
        print(f"[Task: {task['name']}]")
        print(f"Preferred: {task['preferred'].value}")
        if task['alternative']:
            print(f"Fallback: {task['alternative'].value}")
        print(f"Reason: {task['reason']}")

        # Get metadata for chosen object
        metadata = loader.get_object_metadata(task['preferred'])
        print(f"Category: {metadata.category}")
        print()


def example_4_high_level_api_convenience():
    """
    Example 4: High-level API for common tasks
    Shows how convenience API abstracts complexity
    """
    print("\n" + "=" * 90)
    print("EXAMPLE 4: CONVENIENCE API - HIGH-LEVEL ABSTRACTIONS")
    print("=" * 90 + "\n")

    gen = COMPolymorphicCodeGenerator()

    tasks = [
        ("Command Execution", lambda: gen.generate_command_executor("notepad.exe")),
        ("WMI Query", lambda: gen.generate_wmi_query_executor("SELECT * FROM Win32_OperatingSystem")),
        ("Registry Read", lambda: gen.generate_registry_reader("HKCU\\Software\\Microsoft")),
        ("File Operations", lambda: gen.generate_file_operations("open", "C:\\data.xlsx")),
    ]

    for task_name, generator_func in tasks:
        print(f"[{task_name}]")
        code = generator_func()

        # Analyze code
        lines = code.split('\n')
        has_error_handling = "On Error" in code
        has_fallback = "If IsEmpty" in code
        lines_of_code = len([l for l in lines if l.strip()])

        print(f"  Lines of code: {lines_of_code}")
        print(f"  Error handling: {'✓' if has_error_handling else '✗'}")
        print(f"  Fallback chain: {'✓' if has_fallback else '✗'}")
        print(f"  First line: {lines[0][:60]}...")
        print()


def example_5_metadata_driven_selection():
    """
    Example 5: Use metadata to make intelligent decisions
    Shows how metadata enables smart object selection
    """
    print("\n" + "=" * 90)
    print("EXAMPLE 5: METADATA-DRIVEN SELECTION")
    print("=" * 90 + "\n")

    loader = COMPolymorphicLoader()

    print("[Scenario: Select objects that support remote execution]")
    print("-" * 90)

    available_objects = loader.list_available_objects()
    remote_capable = []

    for obj_type_name in available_objects:
        # Get enum
        obj_type = getattr(COMObjectType, obj_type_name.upper().replace('_', '_'))
        metadata = loader.get_object_metadata(obj_type)

        if metadata and metadata.supports_remote:
            remote_capable.append((obj_type_name, metadata.progid))
            print(f"✓ {obj_type_name:<20} ({metadata.progid})")
        else:
            print(f"✗ {obj_type_name:<20} (Local only)")

    print()
    print(f"Total remote-capable objects: {len(remote_capable)}")

    # Show how to use remote capability
    print("\nUsage example:")
    shell = loader.load_object(
        COMObjectType.SHELL,
        use_remote=True,
        remote_machine="192.168.1.100"
    )
    print(shell.get_instantiation_code()[:100] + "...")


def example_6_configuration_export_import():
    """
    Example 6: Export and import configuration
    Shows configuration management capabilities
    """
    print("\n" + "=" * 90)
    print("EXAMPLE 6: CONFIGURATION MANAGEMENT")
    print("=" * 90 + "\n")

    loader = COMPolymorphicLoader()

    # Export configuration
    print("[Exporting loader configuration]")
    config_json = loader.export_to_json()
    config = json.loads(config_json)

    print(f"Available objects: {len(config['available_objects'])}")
    print(f"Objects: {', '.join(config['available_objects'][:5])}...")
    print(f"Fallback chains: {len(config['fallback_chains'])} configured")

    print("\nFallback chain details:")
    for obj, fallbacks in config['fallback_chains'].items():
        if fallbacks:
            print(f"  {obj} -> {' -> '.join(fallbacks)}")

    print("\nVariant information available for:")
    for obj in list(config['variants'].keys())[:3]:
        variant = config['variants'][obj]
        print(f"  {obj}:")
        print(f"    - ProgID: {variant['progid']}")
        print(f"    - CLSID: {variant['clsid'][:20]}...")
        print(f"    - Methods: {len(variant['methods'])} available")


def example_7_creating_custom_workflows():
    """
    Example 7: Create complex workflows using polymorphic loader
    Shows how to build sophisticated automation
    """
    print("\n" + "=" * 90)
    print("EXAMPLE 7: COMPLEX WORKFLOW AUTOMATION")
    print("=" * 90 + "\n")

    gen = COMPolymorphicCodeGenerator()

    print("[Building: System Information Gathering Workflow]")
    print("-" * 90)

    workflow = """
' Step 1: Get system info via WMI
"""
    step1 = gen.generate_wmi_query_executor(
        "SELECT * FROM Win32_OperatingSystem"
    )
    workflow += step1 + "\n\n"

    workflow += """
' Step 2: List running processes
"""
    step2 = gen.generate_wmi_query_executor(
        "SELECT Name, ProcessId FROM Win32_Process"
    )
    workflow += step2 + "\n\n"

    workflow += """
' Step 3: Read registry settings
"""
    step3 = gen.generate_registry_reader(
        "HKCU\\Software\\Microsoft\\Windows"
    )
    workflow += step3

    print(f"Total workflow lines: {len(workflow.split(chr(10)))}")
    print(f"Objects used: WMI (2x), Registry (1x)")
    print("\nFirst 300 characters of workflow:")
    print("-" * 90)
    print(workflow[:300])
    print("...")


def example_8_pattern_implementation():
    """
    Example 8: Implement design patterns with polymorphic loader
    Shows advanced pattern implementation
    """
    print("\n" + "=" * 90)
    print("EXAMPLE 8: DESIGN PATTERNS - STRATEGY PATTERN IMPLEMENTATION")
    print("=" * 90 + "\n")

    loader = COMPolymorphicLoader()

    # Strategy interface
    class ExecutionStrategy:
        def execute(self, command):
            raise NotImplementedError

    # Concrete strategies using polymorphic loader
    class ShellStrategy(ExecutionStrategy):
        def __init__(self, loader):
            self.loader = loader

        def execute(self, command):
            return self.loader.generate_polymorphic_code(
                COMObjectType.SHELL,
                "Run",
                command
            )

    class WMIStrategy(ExecutionStrategy):
        def __init__(self, loader):
            self.loader = loader

        def execute(self, command):
            # Convert to WMI query
            return self.loader.generate_polymorphic_code(
                COMObjectType.WMI_LOCATOR,
                "ExecQuery",
                f"SELECT * FROM Win32_Process WHERE Name='{command}'"
            )

    print("[Implementing Strategy Pattern with Polymorphic Objects]")
    print("-" * 90)

    shell_strategy = ShellStrategy(loader)
    wmi_strategy = WMIStrategy(loader)

    # Use same interface, different strategies
    strategies = [
        ("Shell Strategy", shell_strategy, "calc.exe"),
        ("WMI Strategy", wmi_strategy, "explorer.exe"),
    ]

    for name, strategy, param in strategies:
        print(f"\n[{name}]")
        code = strategy.execute(param)
        print(f"Generated {len(code.split(chr(10)))} lines of code")
        print(f"First line: {code.split(chr(10))[0]}")


def example_9_error_handling_patterns():
    """
    Example 9: Demonstrate error handling patterns
    Shows how to write robust code
    """
    print("\n" + "=" * 90)
    print("EXAMPLE 9: ERROR HANDLING PATTERNS")
    print("=" * 90 + "\n")

    loader = COMPolymorphicLoader()

    print("[Pattern 1: Automatic Error Handling via Fallback]")
    print("-" * 90)
    code = loader.generate_polymorphic_code(
        COMObjectType.SHELL,
        "Run",
        "cmd.exe",
        fallback=True,
        use_error_handling=True
    )
    print("Features:")
    print("✓ On Error Resume Next (handles errors gracefully)")
    print("✓ Automatic fallback to WMI if Shell fails")
    print("✓ On Error GoTo 0 (clears error state)")

    print("\n[Pattern 2: Manual Error Checking]")
    print("-" * 90)
    manual_code = """
On Error Resume Next

Set shell = CreateObject("WScript.Shell")

If Err.Number <> 0 Then
    ' Handle error
    WScript.Echo "Shell creation failed"
    Set wmi = CreateObject("WbemScripting.SWbemLocator")
Else
    shell.Run "cmd.exe"
End If

On Error GoTo 0
"""
    print(manual_code)


def run_all_examples():
    """Run all integration examples"""
    examples = [
        example_1_same_code_multiple_objects,
        example_2_fallback_chain_resilience,
        example_3_dynamic_object_selection,
        example_4_high_level_api_convenience,
        example_5_metadata_driven_selection,
        example_6_configuration_export_import,
        example_7_creating_custom_workflows,
        example_8_pattern_implementation,
        example_9_error_handling_patterns,
    ]

    print("\n" + "=" * 90)
    print("COM POLYMORPHIC LOADER - INTEGRATION EXAMPLES")
    print(f"Total Examples: {len(examples)}")
    print("=" * 90)

    for idx, example_func in enumerate(examples, 1):
        try:
            example_func()
        except Exception as e:
            print(f"\n!!! Error in {example_func.__name__}: {e}")

    print("\n" + "=" * 90)
    print("ALL EXAMPLES COMPLETED")
    print("=" * 90 + "\n")


if __name__ == "__main__":
    run_all_examples()
