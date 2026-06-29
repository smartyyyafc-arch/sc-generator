# Quick Reference - PyArmor and PyInstaller Commands

This is a quick reference guide for the most important commands for code protection.

---

## INSTALLATION

### Install PyArmor
```bash
pip install pyarmor
```

### Install PyInstaller
```bash
pip install pyinstaller
```

### Verify Installation
```bash
pyarmor --version
pyinstaller --version
```

---

## OBFUSCATION (PyArmor)

### Basic Obfuscation
```bash
pyarmor obfuscate your_script.py
```

### Obfuscation with All Protections
```bash
pyarmor obfuscate \
    --obf all \
    --restrict all \
    --capsule \
    --advanced \
    --output obfuscated_code \
    your_script.py
```

### Explanation of Options
- `--obf all` = Obfuscate all code (functions, variables, strings)
- `--restrict all` = Prevent debugging and introspection
- `--capsule` = Use encryption capsule for maximum security
- `--advanced` = Enable advanced obfuscation techniques
- `--output directory` = Write obfuscated code to this directory
- `your_script.py` = Path to your source code

---

## PACKAGING (PyInstaller)

### Create Single-File Executable
```bash
pyinstaller --onefile your_script.py
```

### Create Executable with All Options
```bash
pyinstaller \
    --name="MyApplication" \
    --onefile \
    --distpath="output/dist" \
    --buildpath="output/build" \
    --specpath="output" \
    your_script.py
```

### Explanation of Options
- `--name="AppName"` = Name for the executable
- `--onefile` = Create single executable file (not folder)
- `--windowed` = Hide console window (for GUI apps)
- `--distpath="dir"` = Output directory for executables
- `--buildpath="dir"` = Build temporary directory
- `--specpath="dir"` = Save spec file here
- `your_script.py` = Path to your Python script

---

## COMPLETE WORKFLOW

### Step 1: Obfuscate Your Code
```bash
pyarmor obfuscate \
    --obf all \
    --restrict all \
    --capsule \
    --advanced \
    --output obfuscated_code \
    source_code.py
```

### Step 2: Package the Obfuscated Code
```bash
pyinstaller \
    --name="ProtectedApp" \
    --onefile \
    --distpath="dist" \
    obfuscated_code/source_code.py
```

### Step 3: Run the Executable
```bash
# On Linux/Mac:
./dist/ProtectedApp

# On Windows:
dist\ProtectedApp.exe
```

---

## COMMON OBFUSCATION OPTIONS

| Option | Purpose | Example |
|--------|---------|---------|
| `--obf all` | Obfuscate all code | `--obf all` |
| `--obf no` | No obfuscation | `--obf no` |
| `--restrict all` | Restrict debugging | `--restrict all` |
| `--capsule` | Encryption capsule | `--capsule` |
| `--advanced` | Advanced techniques | `--advanced` |
| `--mix-str` | Encrypt strings | `--mix-str` |
| `--output dir` | Output directory | `--output dist` |

---

## COMMON PYINSTALLER OPTIONS

| Option | Purpose | Example |
|--------|---------|---------|
| `--onefile` | Single file executable | `--onefile` |
| `--windowed` | No console window | `--windowed` |
| `--icon file` | Application icon | `--icon app.ico` |
| `--add-data` | Include extra files | `--add-data src:dest` |
| `--name` | Executable name | `--name MyApp` |
| `--distpath` | Output directory | `--distpath dist` |

---

## EXAMPLES

### Example 1: Protect a Single File
```bash
# Create source code
echo "print('Hello, World!')" > hello.py

# Obfuscate
pyarmor obfuscate --output obf hello.py

# Package
pyinstaller --onefile obf/hello.py

# Output: dist/hello (Linux/Mac) or dist/hello.exe (Windows)
```

### Example 2: Protect with License Verification
```bash
# Obfuscate with maximum protection
pyarmor obfuscate \
    --obf all \
    --restrict all \
    --capsule \
    --advanced \
    --output protected \
    myapp.py

# Package as single file
pyinstaller \
    --name="LicensedApp" \
    --onefile \
    protected/myapp.py

# Run with license key
export LICENSE_KEY="your-license-key"
./dist/LicensedApp
```

### Example 3: Professional Packaging
```bash
# Obfuscate with all protections
pyarmor obfuscate \
    --obf all \
    --restrict all \
    --capsule \
    --advanced \
    --output dist/obfuscated \
    src/main.py

# Package for distribution
pyinstaller \
    --name="ProApplication" \
    --onefile \
    --distpath="dist/executable" \
    --icon="src/app.ico" \
    dist/obfuscated/main.py

# Result: dist/executable/ProApplication.exe
```

---

## TROUBLESHOOTING

### "pyarmor: command not found"
**Solution:** Install PyArmor using: `pip install pyarmor`

### "pyinstaller: command not found"
**Solution:** Install PyInstaller using: `pip install pyinstaller`

### "Permission denied" running executable
**Solution (Linux/Mac):** Make executable with: `chmod +x executable_name`

### "Obfuscated code won't import"
**Solution:** Some code patterns may not work with obfuscation. Test obfuscated code before packaging.

### "Executable is very large (100MB+)"
**Solution:** This is normal. PyInstaller includes Python runtime (~30MB) and dependencies.

### "Antivirus blocks executable"
**Solution:** Sign your executable with a code-signing certificate.

---

## BEST PRACTICES

1. **Always test obfuscated code** - Ensure it works before packaging
2. **Use both PyArmor and PyInstaller** - Obfuscation + packaging = better protection
3. **Add license verification** - Control who can use your code
4. **Implement anti-tampering checks** - Detect unauthorized modifications
5. **Keep source code secure** - Never distribute obfuscated or original code
6. **Only distribute executables** - Standalone binaries are your final product
7. **Sign executables** - Use code-signing to prevent warnings
8. **Version your code** - Track changes to protected versions

---

## RESOURCES

- PyArmor Documentation: https://pyarmor.readthedocs.io/
- PyInstaller Documentation: https://pyinstaller.org/
- GitHub PyArmor: https://github.com/dashingsoft/pyarmor
- GitHub PyInstaller: https://github.com/pyinstaller/pyinstaller

---

## AUTOMATION

Run the complete workflow automatically:

### Using Python Script
```bash
cd /home/user/sc-generator/code-protection-guide
python3 workflow.py
```

### Using Bash Script
```bash
cd /home/user/sc-generator/code-protection-guide
bash run-complete-workflow.sh
```

Both scripts automate all steps from source code to protected executable.
