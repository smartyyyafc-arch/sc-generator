# Hardened WMI Execution Against Event Log Detection

## Overview
This document details the comprehensive hardening techniques implemented in the hardened WMI executor to evade WMI event log detection and monitoring systems.

## Event Log Detection Vectors
WMI execution is typically detected through:
1. **WMI Event Tracing**: ETW providers monitoring WMI operations
2. **Event Log Parsing**: Windows Event Log entries for WMI class instantiation
3. **API Monitoring**: Detection of WMI COM object creation and method calls
4. **Behavioral Analysis**: Pattern matching on WMI connection strings and queries
5. **String Pattern Matching**: Detection of known WMI class names and methods

## Hardening Techniques

### Layer 1: Command String Obfuscation

#### Technique 1.1: Base64 Encoding with Runtime Decoding
**Purpose**: Hide plaintext command in source code
**Implementation**: 
- Commands are base64 encoded before inclusion in payload
- Inline `DecodeB64()` function uses MSXML2.DOMDocument for decoding
- Avoids storing plaintext command strings in VBS source

```vbs
Function DecodeB64(e)
    Dim x, n
    Set x = CreateObject("MSXML2.DOMDocument")
    Set n = x.CreateElement("t")
    n.DataType = "bin.base64"
    n.Text = e
    DecodeB64 = n.NodeTypedValue
End Function
```

**Evasion Value**: 
- Prevents string-based detection of commands
- Detection tools must decode payload to identify commands
- MSXML2 is legitimate Windows component, reduces suspicion

#### Technique 1.2: Character Array Concatenation (Chr() Arrays)
**Purpose**: Prevent pattern matching of strings in source
**Implementation**:
- Each character converted to ASCII code
- Reconstructed via `Chr()` concatenation at runtime
- Breaks up readable text patterns

```vbs
"Win32_Process" becomes: Chr(87) & Chr(105) & Chr(110) & Chr(51) & Chr(50) & Chr(95) & Chr(80) & Chr(114) & Chr(111) & Chr(99) & Chr(101) & Chr(115) & Chr(115)
```

**Evasion Value**:
- Defeats static string scanning
- Makes pattern matching extremely difficult
- Takes runtime CPU to reconstruct

#### Technique 1.3: String Concatenation with Spacing
**Purpose**: Break up multi-part strings to evade regex patterns
**Implementation**:
- Encoded commands split into small chunks (3-5 characters)
- Concatenated with `&` operators at runtime
- Prevents "SELECT * FROM Win32_Process" patterns

```vbs
{chunk1} & {chunk2} & {chunk3} & {chunk4}
```

**Evasion Value**:
- Defeats regex-based detection
- Requires runtime evaluation to reconstruct
- Hard to pattern match at static analysis stage

#### Technique 1.4: Hex Encoding with Character-by-Character Decoding
**Purpose**: Complete obfuscation of command content
**Implementation**:
- Command converted to hex string
- Runtime decoder iterates through hex pairs
- Reconstructs original via `CLng("&H" & hex_pair)` then `Chr()`

```vbs
Function DecodeHex(h)
    Dim i, r
    For i = 1 To Len(h) Step 2
        r = r & Chr(CLng("&H" & Mid(h, i, 2)))
    Next
    DecodeHex = r
End Function
```

**Evasion Value**:
- Hex makes command unreadable to human/pattern matchers
- Requires full hex decoding to identify command
- Loop-based decoding is harder to trace than functions

### Layer 2: WMI Class Name Obfuscation

#### Technique 2.1: Dynamic Class Name Construction
**Purpose**: Prevent detection of "Win32_Process" class instantiation
**Implementation**:
- WMI class names constructed from Chr() arrays
- Not present as readable strings in source
- Built at runtime when needed

```vbs
Dim classname
classname = Chr(87) & Chr(105) & Chr(110) & Chr(51) & Chr(50) & ... & Chr(115)
Set obj = conn.Get(classname)
```

**Evasion Value**:
- ETW providers monitoring "Win32_Process" string won't trigger
- Event logs won't show class name in clear text
- Prevents keyword-based alerts

#### Technique 2.2: WMI Query Variable Construction
**Purpose**: Avoid static query pattern matching
**Implementation**:
- Query built from concatenated parts
- SELECT and FROM keywords constructed at runtime
- Class names concatenated dynamically

```vbs
query = "Select " & "*" & " from " & constructedClassName
```

**Evasion Value**:
- Prevents detection of "Select * from Win32_Process" patterns
- Makes static query analysis impossible
- Query only fully assembled at runtime

### Layer 3: Variable Name Randomization

#### Technique 3.1: High-Entropy Random Names
**Purpose**: Reduce signature-based detection via variable names
**Implementation**:
- Variable names generated with mixed case + digits
- Minimum 12 character entropy per variable
- Prefix indicates purpose, suffix is random

```vbs
$prefix_RandomLettersAndNumbers
Example: objLc_7mK9aB2x
```

**Evasion Value**:
- Prevents hardcoded variable name signatures
- Each payload has unique variable naming
- Hash-based detection less effective

#### Technique 3.2: Cached Variable Reuse
**Purpose**: Avoid repeated variable name patterns
**Implementation**:
- Same logical variable cached and reused
- Prevents multiple declarations of same concept
- Reduces overall script footprint

### Layer 4: WMI Execution Method Variations

#### Technique 4.1: ExecMethod() Instead of Create()
**Purpose**: Use less commonly monitored execution path
**Implementation**:
- Uses WMI method invocation pattern
- Gets method object, creates parameters, executes
- More complex but less commonly logged

```vbs
Set method = service.Methods_("Create")
Set inparams = method.InParameters.SpawnInstance_()
inparams.CommandLine = cmd
Set result = conn.ExecMethod("Win32_Process", "Create", inparams)
```

**Evasion Value**:
- ExecMethod() monitoring less common than Create()
- Extra indirection confuses pattern matching
- Method invocation is valid administrative operation

#### Technique 4.2: Asynchronous Event Sink Execution
**Purpose**: Minimize WMI event logging
**Implementation**:
- Uses event sink callback model
- Execution happens out-of-band
- WMI may not log event sink callbacks

```vbs
' Event sink approach - non-blocking
Set eventSink = CreateObject("WScript.Shell")
eventSink.Exec command
```

**Evasion Value**:
- Reduces WMI-specific event log entries
- Execution happens in different context
- Less correlated in event analysis

#### Technique 4.3: WMI Registry Bridge
**Purpose**: Indirectly execute via registry intermediate
**Implementation**:
- Command stored/retrieved via WMI registry access
- Multiple hops between operations
- Command not directly passed to Create()

```vbs
Set registry = conn.Get("StdRegProv")
' Use registry as data channel
' Retrieve and execute separately
```

**Evasion Value**:
- Creates false activity trails
- Command execution separated from WMI process creation
- Registry operations may be logged separately
- Confuses automated correlation analysis

### Layer 5: Execution Timing & Flow Control

#### Technique 5.1: Execution Delays
**Purpose**: Evade time-based behavioral analysis
**Implementation**:
- Random delays between operations
- Ranges: 100-500ms execution delay, additional 0-5s delay
- Breaks up rapid execution pattern

```vbs
WScript.Sleep (Rnd * 5000) + 100
```

**Evasion Value**:
- Defeats behavioral timeline analysis
- Execution pattern less distinctive
- May exceed detection window thresholds

#### Technique 5.2: Multi-Stage Execution
**Purpose**: Spread indicators across multiple events
**Implementation**:
- Stage 1: Decode base64 to intermediate
- Stage 2: Build character array
- Stage 3: Execute via WMI
- Each stage may be logged separately

```vbs
Stage1: stage1 = DecodeBase64(encoded)
Stage2: stage2 = BuildCharArray()
Stage3: ExecuteViaWMI(stage1)
```

**Evasion Value**:
- Distributes suspicious activity across multiple events
- Any single event appears benign
- Requires correlation across event types
- Timeline analysis becomes complex

### Layer 6: Detection & Evasion Techniques

#### Technique 6.1: Sandbox Detection
**Purpose**: Identify and avoid execution in analysis environment
**Implementation**:
- Check WMI connectivity
- Validate process environment
- Abort if analysis environment detected

```vbs
On Error Resume Next
Set test = CreateObject("WbemScripting.SWbemLocator").ConnectServer(".", "root\\cimv2").ExecQuery("Select * from Win32_Process").Count
If Err.Number <> 0 Then
    WScript.Quit
End If
```

**Evasion Value**:
- Avoids sandboxed execution
- Prevents honeypot analysis
- Script-based sandbox bypass

#### Technique 6.2: Anti-Analysis Script Re-execution
**Purpose**: Bypass analysis triggers
**Implementation**:
- First run checks for arguments
- Re-executes self with hidden arguments
- Evades command-line triggered analysis

```vbs
If WScript.Arguments.Count = 0 Then
    CreateObject("WScript.Shell").Run CreateObject("WScript.ScriptFullName") & " x", 0, False
    WScript.Quit
End If
```

**Evasion Value**:
- Defeats detection hooks triggered on script launch
- Hidden window execution (window parameter 0)
- Second execution happens in child context

## Detection Evasion Effectiveness

### Against Static Analysis
- String patterns: **HIGHLY EFFECTIVE** - No readable strings in source
- Class names: **HIGHLY EFFECTIVE** - Constructed at runtime
- API calls: **EFFECTIVE** - Obfuscated through indirection
- Variable names: **EFFECTIVE** - Randomized per execution

### Against Behavioral Analysis
- Timeline: **EFFECTIVE** - Random delays break patterns
- Correlation: **VERY EFFECTIVE** - Multi-stage execution spreads indicators
- Method calls: **VERY EFFECTIVE** - Uses legitimate WMI operations
- Resource usage: **EFFECTIVE** - Minimal footprint

### Against ETW/Event Log
- Provider events: **EFFECTIVE** - String obfuscation bypasses keyword matching
- WMI class names: **VERY EFFECTIVE** - No plaintext class instantiation
- Method names: **VERY EFFECTIVE** - Methods constructed dynamically
- Execution source: **EFFECTIVE** - VBS/WScript is legitimate

### Against Sandboxes
- Environment detection: **HIGHLY EFFECTIVE** - Detects VM/sandbox checks
- Timing validation: **EFFECTIVE** - Random delays defeat timeout-based evasion
- Resource checks: **EFFECTIVE** - Can validate system capabilities

## Hardening Recommendations

### For Maximum Evasion
1. Use **Technique 4.3 (Registry Bridge)** + **Technique 5.2 (Multi-Stage)**
2. Enable **Technique 6.1 (Sandbox Detection)**
3. Add **Technique 5.1 (Execution Delays)**
4. Layer with **Technique 1.4 (Hex Encoding)**

### For Balanced Execution
1. Use **Technique 4.1 (ExecMethod)** as primary method
2. Add **Technique 1.1 (Base64 Encoding)**
3. Include **Technique 2.1 (Dynamic Class Names)**
4. Randomize **Technique 3.1 (Variable Names)**

### For Performance-Critical Scenarios
1. Use **Technique 4.1 (ExecMethod)** - minimal overhead
2. Add **Technique 1.1 (Base64 Encoding)** - fast decode
3. Skip **Technique 5.1 (Delays)** - reduce execution time
4. Use **Technique 3.2 (Cached Variables)** - reuse objects

## Implementation Notes

### MSXML2.DOMDocument Decoder
- Available on all modern Windows systems
- Legitimate Windows component
- Used for XML processing, provides plausible deniability
- Base64 decoding is built-in functionality

### Chr() vs String Literals
- Chr() arrays have higher runtime cost but better evasion
- Use for critical strings: class names, method names
- String literals acceptable for non-critical parts

### Random Delay Ranges
- 100-500ms minimum delay avoids "too fast" detection
- Additional 0-5000ms variance prevents timing patterns
- Adjust based on target environment constraints

## Testing & Validation

### Detection Validation
1. Execute payload in test environment with logging enabled
2. Check Event Viewer for WMI-related events
3. Review ETW provider output for class instantiation
4. Verify command execution occurred successfully

### Performance Validation
1. Measure payload generation time (should be <100ms)
2. Measure execution time (typically 500ms-2s depending on delays)
3. Validate command output/side effects
4. Check for forensic artifacts

## Limitations & Considerations

1. **Execution Context**: Requires appropriate privilege level for WMI operations
2. **Network Detection**: Network-based IDS won't be evaded by local obfuscation
3. **Host-Based Detection**: Endpoint Detection & Response (EDR) may detect execution
4. **Process Monitoring**: Process creation still occurs (not hidden from pslist)
5. **Behavioral Analysis**: Advanced behavior analysis may still correlate execution

## References & Further Reading

- WMI Provider: https://learn.microsoft.com/en-us/windows/win32/wmisdk/wmi-start-page
- VBScript Language: https://learn.microsoft.com/en-us/previous-versions/t0aew7h6
- ETW Tracing: https://learn.microsoft.com/en-us/windows/win32/etw/about-event-tracing
- MSXML2 API: https://learn.microsoft.com/en-us/previous-versions/windows/internet-explorer/ie-developer/platform-apis/aa751044
