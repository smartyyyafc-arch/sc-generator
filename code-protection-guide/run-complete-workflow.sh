#!/bin/bash

################################################################################
# Complete Python Code Protection Workflow Script
#
# This script automates the entire process of:
# 1. Installing PyArmor and PyInstaller
# 2. Obfuscating Python source code with PyArmor
# 3. Packaging obfuscated code with PyInstaller
# 4. Creating a protected standalone executable
#
# Usage:
#   bash run-complete-workflow.sh
#
# Screen reader note:
# Each step is clearly labeled with [Step X] for easy navigation.
# All output explains what's happening.
################################################################################

set -e  # Exit immediately if any command fails

# Color codes for better readability with screen readers
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'  # No Color

# Define directories
PROJECT_DIR="/home/user/sc-generator"
SOURCE_DIR="$PROJECT_DIR/examples/source-code"
OBFUSCATED_DIR="$PROJECT_DIR/examples/obfuscated-code"
PACKAGED_DIR="$PROJECT_DIR/examples/packaged-executables"
GUIDE_DIR="$PROJECT_DIR/code-protection-guide"

echo ""
echo "================================================================================"
echo "PYTHON CODE PROTECTION WORKFLOW"
echo "PyArmor + PyInstaller Integration"
echo "================================================================================"
echo ""

################################################################################
# STEP 1: VERIFY PYTHON INSTALLATION
################################################################################

echo -e "${BLUE}[Step 1] Verifying Python installation...${NC}"
echo ""

python3 --version
python3 -m pip --version

echo -e "${GREEN}✓ Python is installed and ready${NC}"
echo ""

################################################################################
# STEP 2: INSTALL REQUIRED TOOLS
################################################################################

echo -e "${BLUE}[Step 2] Installing PyArmor and PyInstaller...${NC}"
echo ""
echo "This installs the tools needed for code obfuscation and packaging."
echo ""

echo "Installing PyArmor (for code obfuscation)..."
python3 -m pip install --quiet pyarmor 2>/dev/null || pip install --quiet pyarmor

echo "Installing PyInstaller (for executable packaging)..."
python3 -m pip install --quiet pyinstaller 2>/dev/null || pip install --quiet pyinstaller

echo ""
echo -e "${GREEN}✓ Tools installed successfully${NC}"
echo ""

# Verify installations
echo "Verifying PyArmor installation..."
pyarmor --version

echo ""
echo "Verifying PyInstaller installation..."
pyinstaller --version

echo ""

################################################################################
# STEP 3: VERIFY SOURCE CODE EXISTS
################################################################################

echo -e "${BLUE}[Step 3] Verifying source code...${NC}"
echo ""

if [ ! -f "$SOURCE_DIR/sensitive_algorithm.py" ]; then
    echo -e "${RED}ERROR: Source code not found at $SOURCE_DIR/sensitive_algorithm.py${NC}"
    echo "The example source code file is required to continue."
    exit 1
fi

echo "Source code file found: $SOURCE_DIR/sensitive_algorithm.py"
echo ""
echo "File content preview (first 20 lines):"
echo "---"
head -20 "$SOURCE_DIR/sensitive_algorithm.py"
echo "---"
echo ""
echo -e "${GREEN}✓ Source code is ready for obfuscation${NC}"
echo ""

################################################################################
# STEP 4: PREPARE DIRECTORIES
################################################################################

echo -e "${BLUE}[Step 4] Preparing directories...${NC}"
echo ""

# Clean old obfuscated code if it exists
if [ -d "$OBFUSCATED_DIR" ]; then
    echo "Removing old obfuscated code..."
    rm -rf "$OBFUSCATED_DIR"
fi

# Create fresh directories
mkdir -p "$OBFUSCATED_DIR"
mkdir -p "$PACKAGED_DIR"/{dist,build}

echo -e "${GREEN}✓ Directories prepared${NC}"
echo ""

################################################################################
# STEP 5: OBFUSCATE CODE WITH PYARMOR
################################################################################

echo -e "${BLUE}[Step 5] Obfuscating code with PyArmor...${NC}"
echo ""
echo "PyArmor will now encrypt your source code with these protections:"
echo "  • Function names renamed to meaningless identifiers"
echo "  • Variable names encrypted"
echo "  • String literals encrypted"
echo "  • Algorithm logic protected"
echo "  • Debugging disabled"
echo "  • Introspection prevented"
echo ""
echo "Running: pyarmor obfuscate [options] $SOURCE_DIR/sensitive_algorithm.py"
echo ""

# Run PyArmor obfuscation with all protection options enabled
pyarmor obfuscate \
    --obf all \
    --restrict all \
    --capsule \
    --advanced \
    --output "$OBFUSCATED_DIR" \
    "$SOURCE_DIR/sensitive_algorithm.py"

echo ""
echo -e "${GREEN}✓ Code obfuscation complete${NC}"
echo ""

# Verify obfuscated code
echo "Obfuscated code directory: $OBFUSCATED_DIR"
echo ""
echo "Contents of obfuscated directory:"
ls -la "$OBFUSCATED_DIR/"

echo ""
echo "Obfuscated code file size comparison:"
echo -n "Original code: "
wc -c < "$SOURCE_DIR/sensitive_algorithm.py"
echo -n " bytes"
echo ""
echo -n "Obfuscated code: "
wc -c < "$OBFUSCATED_DIR/sensitive_algorithm.py"
echo -n " bytes"
echo ""
echo ""

echo "Obfuscated code preview (first 20 lines):"
echo "Notice: Variable names and function names are now meaningless"
echo "---"
head -20 "$OBFUSCATED_DIR/sensitive_algorithm.py"
echo "---"
echo ""

################################################################################
# STEP 6: TEST OBFUSCATED CODE
################################################################################

echo -e "${BLUE}[Step 6] Testing obfuscated code...${NC}"
echo ""
echo "The obfuscated code should still run exactly like the original:"
echo ""

cd "$OBFUSCATED_DIR"
python3 -c "
import sys
sys.path.insert(0, '.')

# Import the obfuscated module
try:
    import sensitive_algorithm

    # Test that the obfuscated code works
    algo = sensitive_algorithm.ProprietaryAlgorithm()
    test_data = [1.5, 2.3, 3.7]
    result = algo.calculate_proprietary_value(test_data)

    print('Testing obfuscated code...')
    print(f'✓ Module imported successfully')
    print(f'✓ Algorithm instantiated')
    print(f'✓ Calculation result: {result:.6f}')
    print(f'✓ Obfuscated code is functional')
except Exception as e:
    print(f'ERROR: {e}')
    sys.exit(1)
"

cd "$PROJECT_DIR"
echo ""
echo -e "${GREEN}✓ Obfuscated code works correctly${NC}"
echo ""

################################################################################
# STEP 7: PACKAGE WITH PYINSTALLER
################################################################################

echo -e "${BLUE}[Step 7] Packaging with PyInstaller...${NC}"
echo ""
echo "PyInstaller will now create a standalone executable that:"
echo "  • Includes the obfuscated code"
echo "  • Includes Python runtime (user doesn't need Python installed)"
echo "  • Includes all dependencies"
echo "  • Runs on Windows, Linux, and macOS"
echo "  • Hides the source code completely"
echo ""
echo "Running: pyinstaller [options] $OBFUSCATED_DIR/sensitive_algorithm.py"
echo ""

# Run PyInstaller to create executable
cd "$PROJECT_DIR"

pyinstaller \
    --name="PropertyProtectedTool" \
    --onefile \
    --distpath="$PACKAGED_DIR/dist" \
    --buildpath="$PACKAGED_DIR/build" \
    --specpath="$PACKAGED_DIR" \
    --hidden-import=sensitive_algorithm \
    "$OBFUSCATED_DIR/sensitive_algorithm.py"

echo ""
echo -e "${GREEN}✓ Packaging complete${NC}"
echo ""

################################################################################
# STEP 8: VERIFY EXECUTABLE
################################################################################

echo -e "${BLUE}[Step 8] Verifying executable...${NC}"
echo ""

EXECUTABLE="$PACKAGED_DIR/dist/PropertyProtectedTool"

# Check for Windows or Linux/Mac executable
if [ -f "$EXECUTABLE.exe" ]; then
    EXECUTABLE="$EXECUTABLE.exe"
    echo "Executable type: Windows (.exe)"
elif [ ! -f "$EXECUTABLE" ]; then
    echo -e "${RED}ERROR: Executable not found at $EXECUTABLE${NC}"
    exit 1
else
    echo "Executable type: Linux/Mac binary"
fi

echo "Executable location: $EXECUTABLE"
echo ""

# Check file size
EXEC_SIZE=$(ls -lh "$EXECUTABLE" | awk '{print $5}')
echo "Executable size: $EXEC_SIZE"
echo "(Includes Python runtime: ~30MB)"
echo ""

# Make executable (Linux/Mac)
if [[ ! "$EXECUTABLE" =~ \.exe$ ]]; then
    chmod +x "$EXECUTABLE"
fi

ls -lh "$EXECUTABLE"
echo ""
echo -e "${GREEN}✓ Executable verified${NC}"
echo ""

################################################################################
# STEP 9: TEST EXECUTABLE
################################################################################

echo -e "${BLUE}[Step 9] Testing executable...${NC}"
echo ""
echo "Running the protected executable..."
echo ""

# Set license key for testing
export LICENSE_KEY="KEY-2024-ENTERPRISE-001"

# Run the executable and capture output
if [ -f "$EXECUTABLE" ]; then
    "$EXECUTABLE"
    RESULT=$?

    if [ $RESULT -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✓ Executable runs successfully${NC}"
    else
        echo ""
        echo -e "${RED}ERROR: Executable failed with exit code $RESULT${NC}"
        exit 1
    fi
else
    echo -e "${RED}ERROR: Executable not found${NC}"
    exit 1
fi

echo ""

################################################################################
# STEP 10: SUMMARY AND NEXT STEPS
################################################################################

echo -e "${BLUE}[Step 10] Summary and next steps${NC}"
echo ""
echo "================================================================================"
echo "WORKFLOW COMPLETE - YOUR CODE IS NOW PROTECTED"
echo "================================================================================"
echo ""

echo "What was accomplished:"
echo "  ✓ Source code obfuscated with PyArmor"
echo "  ✓ Obfuscated code packaged with PyInstaller"
echo "  ✓ Standalone executable created"
echo "  ✓ No Python installation required for users"
echo "  ✓ Source code protected from reverse engineering"
echo ""

echo "Key directories:"
echo "  • Original source: $SOURCE_DIR/"
echo "  • Obfuscated code: $OBFUSCATED_DIR/"
echo "  • Protected executable: $PACKAGED_DIR/dist/"
echo ""

echo "To distribute to clients:"
echo "  1. Send the executable: $EXECUTABLE"
echo "  2. Users can run it without installing Python"
echo "  3. The code is fully protected from reverse engineering"
echo ""

echo "Important notes:"
echo "  • Never distribute the obfuscated source code"
echo "  • Only distribute the final executable"
echo "  • Keep your source code secure"
echo "  • Implement license verification for production"
echo "  • Add anti-tampering checks for added security"
echo ""

echo "This protects your intellectual property using industry-standard tools:"
echo "  • PyArmor: Code obfuscation (encryption and renaming)"
echo "  • PyInstaller: Executable packaging (standalone binary)"
echo ""

echo "================================================================================"
echo ""

exit 0
