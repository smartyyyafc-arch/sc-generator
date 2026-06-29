# Python Code Protection Guide
## Enterprise-Grade Code Obfuscation and Packaging

This guide provides everything you need to protect Python source code from reverse engineering using industry-standard tools.

---

## WHAT IS INCLUDED

This guide covers:

1. **Code Obfuscation** - Using PyArmor to encrypt and protect source code
2. **Executable Packaging** - Using PyInstaller to create standalone executables
3. **Anti-Tampering Protection** - Detecting unauthorized modifications
4. **License Verification** - Controlling who can use your code
5. **Secure Deployment** - Best practices for distribution and updates

---

## GETTING STARTED

### For Quick Start (5 minutes)

1. Read: `QUICK_REFERENCE.md`
   - Essential commands
   - Copy-paste examples
   - Troubleshooting

### For Complete Workflow (30 minutes)

1. Read: `COMPLETE_WORKFLOW.md`
   - Full step-by-step guide
   - Detailed explanations
   - All options and their meanings

2. Run one of the automation scripts:
   ```bash
   # Option A: Using Python (recommended)
   python3 /home/user/sc-generator/code-protection-guide/workflow.py

   # Option B: Using Bash
   bash /home/user/sc-generator/code-protection-guide/run-complete-workflow.sh
   ```

### For Advanced Features (1+ hours)

1. Read: `ADVANCED_FEATURES.md`
   - Anti-tampering detection
   - License verification systems
   - Server-side security
   - Production deployment

---

## DIRECTORY STRUCTURE

```
/home/user/sc-generator/
├── code-protection-guide/          # This guide
│   ├── README.md                   # (You are here)
│   ├── QUICK_REFERENCE.md          # Command reference
│   ├── COMPLETE_WORKFLOW.md        # Full guide
│   ├── ADVANCED_FEATURES.md        # Advanced techniques
│   ├── workflow.py                 # Automated workflow (Python)
│   └── run-complete-workflow.sh    # Automated workflow (Bash)
│
└── examples/
    ├── source-code/
    │   └── sensitive_algorithm.py  # Example proprietary code
    │
    ├── obfuscated-code/            # Output: Obfuscated code
    │   └── sensitive_algorithm.py  # (Created by PyArmor)
    │
    └── packaged-executables/       # Output: Final executables
        ├── dist/                   # Distribution directory
        │   └── PropertyProtectedTool  # (Created by PyInstaller)
        ├── build/                  # Build directory (temporary)
        └── PropertyProtectedTool.spec # PyInstaller spec file
```

---

## QUICK START: RUN THE AUTOMATED WORKFLOW

The easiest way to understand the complete process is to run the automated workflow:

### Option 1: Python Script (Recommended for screen readers)

```bash
cd /home/user/sc-generator/code-protection-guide
python3 workflow.py
```

This script will:
1. Install PyArmor and PyInstaller
2. Obfuscate the example source code
3. Package into executable
4. Test the protected executable
5. Show you the results

**Output:**
- Obfuscated code in `examples/obfuscated-code/`
- Protected executable in `examples/packaged-executables/dist/`

### Option 2: Bash Script

```bash
cd /home/user/sc-generator/code-protection-guide
bash run-complete-workflow.sh
```

Same results as Python script, but using shell commands.

---

## THE COMPLETE WORKFLOW (3 STEPS)

### Step 1: Obfuscate Your Code with PyArmor

```bash
# Install PyArmor
pip install pyarmor

# Obfuscate your code
pyarmor obfuscate \
    --obf all \
    --restrict all \
    --capsule \
    --advanced \
    --output obfuscated_code \
    your_source_code.py
```

**What PyArmor does:**
- Encrypts bytecode
- Renames functions and variables
- Disables debugging and introspection
- Adds anti-tampering protection
- Result: Code can't be reverse-engineered

### Step 2: Package with PyInstaller

```bash
# Install PyInstaller
pip install pyinstaller

# Create executable from obfuscated code
pyinstaller \
    --name="YourApp" \
    --onefile \
    --distpath="dist" \
    obfuscated_code/your_source_code.py
```

**What PyInstaller does:**
- Bundles Python interpreter
- Includes all dependencies
- Creates standalone executable (.exe, .bin, or .app)
- No Python installation needed for users
- Result: Single file users can run

### Step 3: Distribute to Clients

```bash
# The executable in dist/ is ready for distribution
# Users can run it directly without any setup
./dist/YourApp

# Or on Windows:
dist\YourApp.exe
```

**Result:**
- Your source code is fully protected
- Users can't reverse-engineer it
- No Python installation needed
- Runs on Windows, Linux, and macOS

---

## KEY CONCEPTS

### What is Code Obfuscation?

Code obfuscation transforms readable code into unreadable code while maintaining functionality.

**Before obfuscation:**
```python
def calculate_price(quantity, price):
    return quantity * price * 0.9
```

**After obfuscation:**
```python
def __0oO0Oo(__1O1o__, __O0O1__):
    return __1O1o__ * __O0O1__ * 0.9
```

**Protection mechanisms:**
- Function names are meaningless
- Variable names are encrypted
- Code flow is obfuscated
- Strings are encrypted
- Debugging is disabled

### Why PyArmor?

PyArmor provides multiple layers of protection:

1. **Encryption** - Bytecode is encrypted
2. **Obfuscation** - Names are renamed
3. **Anti-Debugging** - Debuggers can't attach
4. **Anti-Introspection** - Can't inspect code at runtime
5. **Capsule Security** - Uses encryption capsule for maximum security
6. **Advanced Mode** - Multiple obfuscation passes

### Why PyInstaller?

PyInstaller creates standalone executables:

1. **Single File** - No separate files to distribute
2. **Bundled Runtime** - Includes Python interpreter
3. **Dependencies Included** - All libraries bundled
4. **Cross-Platform** - Works on Windows, Linux, macOS
5. **No Installation** - Users just run the executable
6. **Secure Distribution** - No source code exposed

---

## DOCUMENTATION

### Main Guides

| Document | Purpose | Read Time | Best For |
|----------|---------|-----------|----------|
| `QUICK_REFERENCE.md` | Command reference | 5 min | Quick lookup |
| `COMPLETE_WORKFLOW.md` | Full guide with explanations | 20 min | Learning |
| `ADVANCED_FEATURES.md` | Advanced techniques | 30+ min | Production |

### Example Code

| File | Purpose |
|------|---------|
| `examples/source-code/sensitive_algorithm.py` | Example proprietary code |
| `code-protection-guide/workflow.py` | Python automation script |
| `code-protection-guide/run-complete-workflow.sh` | Bash automation script |

---

## COMMON TASKS

### Task 1: Protect a Single Python File

```bash
# Step 1: Obfuscate
pyarmor obfuscate \
    --obf all \
    --restrict all \
    --output protected \
    myapp.py

# Step 2: Package
pyinstaller --onefile protected/myapp.py

# Result: dist/myapp (or dist/myapp.exe on Windows)
```

### Task 2: Protect Multiple Files

```bash
# Step 1: Create package structure
mkdir mypackage
cp *.py mypackage/
touch mypackage/__init__.py

# Step 2: Obfuscate entire package
pyarmor obfuscate \
    --obf all \
    --restrict all \
    --output protected \
    mypackage

# Step 3: Package
pyinstaller \
    --onefile \
    --name="MyApp" \
    protected/mypackage/__main__.py

# Result: dist/MyApp
```

### Task 3: Add License Verification

See `ADVANCED_FEATURES.md` for complete license verification system.

Quick example:
```python
# In your main.py (before obfuscation)

from license_manager import verify_license

def main():
    # Verify license first
    verify_license()

    # Then run your code
    print("Application running with valid license")

if __name__ == "__main__":
    main()
```

### Task 4: Add Anti-Tampering Protection

See `ADVANCED_FEATURES.md` for complete anti-tampering system.

Quick example:
```python
# In your main.py (before obfuscation)

from anti_tampering import verify_at_startup

def main():
    # Verify integrity first
    verify_at_startup()

    # Then run your code
    print("Code integrity verified")

if __name__ == "__main__":
    main()
```

---

## IMPORTANT NOTES

### Installation Requirements

Before you start, make sure you have:
- Python 3.7 or higher
- pip (Python package manager)
- PyArmor (installed via pip)
- PyInstaller (installed via pip)

### Free vs Paid PyArmor

PyArmor offers:
- **Free version**: Basic obfuscation (sufficient for most uses)
- **Paid version**: Advanced features and license options

Both versions work with this guide.

### Limitations to Know

1. **Obfuscation is not perfect security**
   - Determined reverse engineers CAN crack it
   - Use as PART of your security strategy
   - Add license verification and updates

2. **Performance impact**
   - Obfuscated code runs 5-20% slower
   - Not suitable for real-time systems
   - Acceptable for most applications

3. **Debugging complexity**
   - Can't easily debug obfuscated code
   - Keep non-obfuscated version during development
   - Obfuscate only for distribution

4. **Executable size**
   - PyInstaller adds ~30MB (Python runtime)
   - Typical executables: 50-100MB+
   - Size depends on dependencies

### Best Practices

1. **Always test obfuscated code** - Ensure it works before packaging
2. **Use both PyArmor + PyInstaller** - Layered protection is best
3. **Implement license verification** - Control who uses your code
4. **Sign your executables** - Prevents antivirus warnings
5. **Keep source code secure** - Never distribute code or archives
6. **Version your releases** - Track changes
7. **Provide updates** - Patch security issues promptly
8. **Add anti-tampering checks** - Detect unauthorized modifications

---

## TROUBLESHOOTING

### Problem: "pyarmor: command not found"
**Solution:** Run `pip install pyarmor`

### Problem: "pyinstaller: command not found"
**Solution:** Run `pip install pyinstaller`

### Problem: "Obfuscated code won't run"
**Solution:** Some code patterns don't work with obfuscation. Test before packaging.

### Problem: "Executable is very large (100MB+)"
**Solution:** This is normal. Includes Python runtime (~30MB) + dependencies.

### Problem: "Antivirus flags my executable"
**Solution:** Sign your executable with a code-signing certificate.

### Problem: "Permission denied running executable"
**Solution (Linux/Mac):** Run `chmod +x executable_name`

For more troubleshooting, see `QUICK_REFERENCE.md`.

---

## NEXT STEPS

1. **Read the Quick Reference**
   - `QUICK_REFERENCE.md` - 5 minute overview

2. **Run the Automated Workflow**
   - `python3 workflow.py` - See it working

3. **Read the Complete Guide**
   - `COMPLETE_WORKFLOW.md` - Detailed explanations

4. **Protect Your Code**
   - Apply to your own source code

5. **Learn Advanced Features**
   - `ADVANCED_FEATURES.md` - License verification, anti-tampering

---

## RESOURCES

### Official Documentation
- PyArmor Docs: https://pyarmor.readthedocs.io/
- PyInstaller Docs: https://pyinstaller.org/

### GitHub Repositories
- PyArmor: https://github.com/dashingsoft/pyarmor
- PyInstaller: https://github.com/pyinstaller/pyinstaller

### Related Tools
- Code signing (Windows): Signtool
- Code signing (macOS): codesign
- Executable signing (macOS): spctl

---

## ABOUT THIS GUIDE

**This guide is designed for screen reader accessibility:**
- Clear section headers for navigation
- Detailed explanations of all steps
- Well-commented code examples
- Command-line options explained
- Step-by-step instructions
- Complete automation scripts

**Included Tools:**
- `workflow.py` - Fully automated, screen reader friendly
- `run-complete-workflow.sh` - Bash alternative
- Example code with detailed comments
- Quick reference for common tasks

---

## GETTING HELP

If you encounter issues:

1. **Check QUICK_REFERENCE.md** - Troubleshooting section
2. **Read COMPLETE_WORKFLOW.md** - Detailed explanations
3. **Review examples/** - Working example code
4. **Check official docs** - PyArmor and PyInstaller websites

---

## SUMMARY

**To protect your Python code:**

1. Install: `pip install pyarmor pyinstaller`
2. Obfuscate: `pyarmor obfuscate --obf all --output dist your_code.py`
3. Package: `pyinstaller --onefile dist/your_code.py`
4. Distribute: Send the executable from `dist/` to users

That's it. Your code is now protected from reverse engineering using industry-standard tools.

---

## EXAMPLE WORKFLOW

```bash
# 1. Create source code (or use existing)
cp myapp.py source-code/

# 2. Obfuscate with PyArmor
pyarmor obfuscate \
    --obf all \
    --restrict all \
    --capsule \
    --advanced \
    --output obfuscated-code \
    source-code/myapp.py

# 3. Package with PyInstaller
pyinstaller \
    --name="MyApplication" \
    --onefile \
    --distpath="executables/dist" \
    obfuscated-code/myapp.py

# 4. Distribute to clients
# Send: executables/dist/MyApplication (or .exe on Windows)
```

---

**Start with `QUICK_REFERENCE.md` for immediate results, or run `workflow.py` to see everything in action.**
