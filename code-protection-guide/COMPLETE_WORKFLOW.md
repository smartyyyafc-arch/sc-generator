# Complete Python Code Protection Workflow
## PyArmor + PyInstaller Integration Guide

This guide explains how to protect Python source code using industry-standard tools:
- **PyArmor**: For code obfuscation (protecting source code from reverse engineering)
- **PyInstaller**: For packaging obfuscated code into standalone executables

---

## PART 1: INSTALLATION

### Install PyArmor (Code Obfuscation Tool)

PyArmor is a commercial tool for obfuscating Python code. This protects your intellectual property.

```bash
# Install PyArmor using pip
pip install pyarmor

# Verify installation - this should show the version
pyarmor --version
```

**What PyArmor does:**
- Encrypts Python bytecode
- Renames variables and functions to meaningless names
- Adds anti-tampering protection
- Prevents debugging and introspection
- Creates obfuscated code that runs normally but can't be reverse-engineered

### Install PyInstaller (Packaging Tool)

PyInstaller bundles Python code and all dependencies into a standalone executable.

```bash
# Install PyInstaller using pip
pip install pyinstaller

# Verify installation - this should show the version
pyinstaller --version
```

**What PyInstaller does:**
- Converts Python scripts into Windows .exe, Linux binaries, or macOS apps
- Includes all Python dependencies in the executable
- Creates single-file executables or directories with dependencies
- Hides the Python interpreter from end users
- Works cross-platform

---

## PART 2: PREPARE YOUR PYTHON CODE

You need source code to protect. Create a simple example:

**Example: sensitive_algorithm.py**
This represents your proprietary code that needs protection.

```python
# File: sensitive_algorithm.py
# This is your proprietary code that needs protection

def calculate_proprietary_algorithm(data):
    """
    This is your secret algorithm that competitors are stealing.
    In real scenarios, this would be complex IP.
    """
    result = 0
    for value in data:
        # Complex proprietary calculation
        result += (value ** 2) * 0.75
    return result


def validate_license(license_key):
    """
    License verification - protected by obfuscation.
    """
    # In real scenarios, this would verify against a server
    valid_keys = ['KEY-2024-ENTERPRISE', 'KEY-2024-PROFESSIONAL']
    return license_key in valid_keys


def process_data(input_file, output_file):
    """
    Main processing function.
    This represents your proprietary data processing logic.
    """
    print("Processing data with proprietary algorithm...")
    
    # Read data
    with open(input_file, 'r') as f:
        data = [float(line.strip()) for line in f.readlines()]
    
    # Apply proprietary algorithm
    result = calculate_proprietary_algorithm(data)
    
    # Write output
    with open(output_file, 'w') as f:
        f.write(f"Result: {result}\n")
    
    print(f"Processing complete. Result written to {output_file}")
    return result


if __name__ == "__main__":
    # Entry point when run as standalone executable
    print("Proprietary Algorithm Tool v1.0")
    print("This code is protected by PyArmor encryption")
    
    # Verify license
    license_key = 'KEY-2024-ENTERPRISE'
    if not validate_license(license_key):
        print("ERROR: Invalid license key")
        exit(1)
    
    print("License verified. Running analysis...")
    
    # Process data
    process_data('input.txt', 'output.txt')
```

Save this as: `examples/source-code/sensitive_algorithm.py`

---

## PART 3: OBFUSCATE WITH PYARMOR

### Step 1: Understand Obfuscation Options

PyArmor provides several protection levels:

| Option | What It Does | Protection Level |
|--------|-------------|-----------------|
| `--obf` | Obfuscate code | Basic |
| `--restrict` | Restrict runtime access | Medium |
| `--capsule` | Use capsule encryption | Strong |
| `--advanced` | Advanced obfuscation | Very Strong |
| `--no-runtime` | Remove Python runtime checks | Maximum |

### Step 2: Create Obfuscated Version

```bash
# Navigate to project directory
cd /home/user/sc-generator

# Command 1: Create obfuscated code with maximum protection
# This creates a 'dist' directory with obfuscated code
pyarmor obfuscate \
    --obf all \
    --restrict all \
    --capsule \
    --advanced \
    --output examples/obfuscated-code \
    examples/source-code/sensitive_algorithm.py

# What this command does:
# --obf all           = Obfuscate all code (functions, variables, strings)
# --restrict all      = Restrict runtime debugging and introspection
# --capsule           = Use encryption capsule for maximum security
# --advanced          = Enable advanced obfuscation techniques
# --output            = Write obfuscated code to this directory
```

### Step 3: Verify Obfuscation

After obfuscation, your code looks like this:

**Before obfuscation:**
```python
def calculate_proprietary_algorithm(data):
    result = 0
    for value in data:
        result += (value ** 2) * 0.75
    return result
```

**After obfuscation (example):**
```python
# Obfuscated code - variable names are meaningless
def __0oo0O0(__1Oo1oO0):
    __O0o1OOO = 0
    for __1O1oOoO0 in __1Oo1oO0:
        __O0o1OOO += (__1O1oOoO0 ** 2) * 0.75
    return __O0o1OOO
```

**What's protected:**
- Function names are renamed
- Variable names are renamed
- Algorithm logic is encrypted
- Strings are encrypted
- Debugging is disabled
- Code inspection tools won't work

---

## PART 4: PACKAGE WITH PYINSTALLER

### Step 1: Prepare for Packaging

PyInstaller needs to know what to include:

```bash
# Create a spec file for maximum control
# This file tells PyInstaller exactly how to build your executable

pyinstaller \
    --name="PropertyProtectedTool" \
    --onefile \
    --windowed \
    --add-data="examples/obfuscated-code:obfuscated_code" \
    --distpath="examples/packaged-executables/dist" \
    --buildpath="examples/packaged-executables/build" \
    --specpath="examples/packaged-executables" \
    examples/obfuscated-code/sensitive_algorithm.py

# What these options do:
# --name="PropertyProtectedTool"  = Name of the executable
# --onefile                       = Create single executable file (not folder)
# --windowed                      = Hide console window (for GUI apps)
# --add-data                      = Include additional files
# --distpath                      = Output directory for executable
# --buildpath                     = Build temporary directory
# --specpath                      = Save spec file here
```

### Step 2: Understand the Build Process

PyInstaller creates:
1. **Source code analysis** - finds all imports and dependencies
2. **Dependency collection** - gathers all required libraries
3. **Bytecode compilation** - compiles Python to bytecode
4. **Executable creation** - packages everything into .exe/.bin/app
5. **Output** - produces standalone executable

### Step 3: Verify the Executable

```bash
# Check if executable was created
ls -la examples/packaged-executables/dist/

# Run the executable (this depends on your OS)
# On Linux/Mac:
./examples/packaged-executables/dist/PropertyProtectedTool

# On Windows:
examples\packaged-executables\dist\PropertyProtectedTool.exe
```

---

## PART 5: ADVANCED OPTIONS FOR MAXIMUM PROTECTION

### Anti-Tampering Protection

Add checksum verification:

```python
# Add this to your main script BEFORE obfuscation
import hashlib
import sys

def verify_integrity():
    """
    Verify that the obfuscated code hasn't been modified.
    This prevents tampering after packaging.
    """
    # This is a placeholder - in production, calculate actual checksum
    EXPECTED_CHECKSUM = "abc123def456"
    
    # Calculate current file checksum
    current_file = sys.argv[0]
    try:
        with open(current_file, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        
        if file_hash != EXPECTED_CHECKSUM:
            print("ERROR: Code has been tampered with!")
            sys.exit(1)
    except:
        pass  # In production, handle errors carefully

# Call this at startup
verify_integrity()
```

### License-Based Execution

Add license verification:

```python
def check_license():
    """
    Verify license before running code.
    License keys should be:
    - Encrypted
    - Time-limited
    - Device-specific
    """
    license_key = os.environ.get('LICENSE_KEY')
    
    if not license_key:
        print("ERROR: No license key provided")
        print("Set environment variable: LICENSE_KEY='your-key'")
        sys.exit(1)
    
    # In production, verify against licensing server
    valid_licenses = validate_with_server(license_key)
    
    if not valid_licenses:
        print("ERROR: Invalid or expired license")
        sys.exit(1)
```

### String Encryption

PyArmor encrypts all strings automatically:

```bash
# Force string encryption with highest security
pyarmor obfuscate \
    --obf all \
    --restrict all \
    --capsule \
    --advanced \
    --mix-str \
    --examples/obfuscated-code \
    examples/source-code/sensitive_algorithm.py

# --mix-str = Encrypt all string literals
```

---

## PART 6: COMPLETE WORKFLOW SUMMARY

Here's the step-by-step process from source code to protected executable:

```
Step 1: Create source code
  └─ Write your proprietary Python code
  └─ Save as: examples/source-code/sensitive_algorithm.py

Step 2: Obfuscate with PyArmor
  └─ Run: pyarmor obfuscate [options] source_file
  └─ Output: examples/obfuscated-code/
  └─ Result: Obfuscated code that can't be reverse-engineered

Step 3: Package with PyInstaller
  └─ Run: pyinstaller [options] obfuscated_file
  └─ Output: examples/packaged-executables/dist/
  └─ Result: Standalone executable (.exe on Windows, binary on Linux)

Step 4: Distribute
  └─ Send executable to clients
  └─ No Python installation required
  └─ No source code visible
  └─ Code protected from reverse engineering
```

---

## PART 7: IMPORTANT LIMITATIONS

**What PyArmor + PyInstaller CANNOT do:**

1. **Perfect security is impossible** - Determined reverse engineers can crack any obfuscation
2. **Performance impact** - Obfuscated code runs 5-20% slower
3. **Debugging issues** - Obfuscated code is harder to debug (use non-obfuscated version for development)
4. **License requirements** - PyArmor is commercial software (free trial available)
5. **Python runtime exposure** - Executables include Python interpreter (about 30MB)

**Best practices:**
- Use obfuscation as PART of your security strategy, not the whole strategy
- Add license verification
- Add anti-tampering checks
- Keep proprietary algorithms server-side when possible
- Use HTTPS for client-server communication
- Implement rate limiting and usage tracking

---

## PART 8: TROUBLESHOOTING

### Issue: "pyarmor: command not found"
**Solution:** PyArmor not installed. Run: `pip install pyarmor`

### Issue: "Permission denied when running executable"
**Solution (Linux/Mac):** Run: `chmod +x executable_name`

### Issue: "Obfuscated code won't run"
**Solution:** Check for import errors. Some advanced features may not work with certain code patterns.

### Issue: "Executable is very large (100MB+)"
**Solution:** This is normal. PyInstaller includes the entire Python runtime (~30MB) plus all dependencies.

### Issue: "Antivirus blocks executable"
**Solution:** Some antivirus software flags packed executables. Sign your executable with a code-signing certificate to fix this.

---

## PART 9: PRODUCTION DEPLOYMENT

When deploying to clients:

1. **Sign your executable**
   ```bash
   # Requires a code-signing certificate
   # This prevents antivirus false positives
   ```

2. **Create an installer**
   ```bash
   # Use NSIS or similar tool to create professional installer
   # Includes license agreement, installation paths, uninstall option
   ```

3. **Implement update mechanism**
   ```python
   # Check for updates on startup
   # Download and install new versions securely
   # Verify checksums before updating
   ```

4. **Monitor usage**
   ```python
   # Log usage data (with user consent)
   # Detect licensing violations
   # Identify reverse-engineering attempts
   ```

---

## SUMMARY

**PyArmor + PyInstaller provides:**
- ✓ Source code obfuscation (prevents reverse engineering)
- ✓ Standalone executables (no Python installation needed)
- ✓ Anti-tampering protection (detect modifications)
- ✓ License enforcement (control who can use your code)
- ✓ Cross-platform support (Windows, Linux, macOS)

**This protects intellectual property by:**
- Encrypting bytecode
- Renaming identifiers
- Disabling debugging
- Bundling into executables
- Adding license verification

**Industry standard use cases:**
- Commercial software
- Licensed tools
- Proprietary algorithms
- SaaS applications
- Enterprise software

This is how legitimate software companies protect their intellectual property.
