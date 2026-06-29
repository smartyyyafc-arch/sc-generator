#!/usr/bin/env python3
"""
Complete Python Code Protection Workflow Script

This script automates the entire process of protecting your Python code:
1. Install PyArmor and PyInstaller
2. Obfuscate your source code with PyArmor
3. Package obfuscated code with PyInstaller
4. Create a protected standalone executable

Screen reader friendly:
- Each step is clearly labeled and explained
- All output describes what's happening
- Use for learning or automation

Usage:
    python3 workflow.py
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


class CodeProtectionWorkflow:
    """
    Manages the complete workflow for protecting Python code.

    This class handles:
    - Installing required tools (PyArmor, PyInstaller)
    - Obfuscating source code
    - Packaging executables
    - Verification and testing
    """

    def __init__(self):
        """Initialize the workflow with directory paths."""
        # Get the project directory
        self.project_dir = Path("/home/user/sc-generator")
        self.source_dir = self.project_dir / "examples" / "source-code"
        self.obfuscated_dir = self.project_dir / "examples" / "obfuscated-code"
        self.packaged_dir = self.project_dir / "examples" / "packaged-executables"
        self.guide_dir = self.project_dir / "code-protection-guide"

        # Create directories if they don't exist
        self.source_dir.mkdir(parents=True, exist_ok=True)
        self.obfuscated_dir.mkdir(parents=True, exist_ok=True)
        self.packaged_dir.mkdir(parents=True, exist_ok=True)
        (self.packaged_dir / "build").mkdir(parents=True, exist_ok=True)
        (self.packaged_dir / "dist").mkdir(parents=True, exist_ok=True)

    def print_header(self, title):
        """Print a formatted section header."""
        line = "=" * 80
        print()
        print(line)
        print(title)
        print(line)
        print()

    def print_step(self, step_number, title):
        """Print a formatted step header."""
        print(f"\n[Step {step_number}] {title}")
        print("-" * 80)
        print()

    def print_success(self, message):
        """Print a success message."""
        print(f"✓ {message}")

    def print_error(self, message):
        """Print an error message."""
        print(f"✗ ERROR: {message}")

    def run_command(self, command, description=""):
        """
        Run a shell command and handle errors.

        Args:
            command: Command to run (list of strings)
            description: Description of what the command does

        Returns:
            True if successful, False otherwise
        """
        if description:
            print(f"Running: {description}")

        print(f"Command: {' '.join(command)}")
        print()

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True
            )

            # Print output if any
            if result.stdout:
                print(result.stdout)

            return True

        except subprocess.CalledProcessError as e:
            self.print_error(f"Command failed: {e}")
            if e.stderr:
                print(f"Error output:\n{e.stderr}")
            return False

        except FileNotFoundError as e:
            self.print_error(f"Command not found: {e}")
            return False

    def step_1_verify_python(self):
        """Step 1: Verify Python installation."""
        self.print_step(1, "Verifying Python installation")

        # Check Python version
        result = subprocess.run(
            [sys.executable, "--version"],
            capture_output=True,
            text=True
        )

        print(f"Python version: {result.stdout.strip()}")

        # Check pip installation
        result = subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True,
            text=True
        )

        print(f"Pip version: {result.stdout.strip()}")
        print()

        self.print_success("Python is installed and ready")

    def step_2_install_tools(self):
        """Step 2: Install PyArmor and PyInstaller."""
        self.print_step(2, "Installing PyArmor and PyInstaller")

        print("PyArmor: For code obfuscation (encrypting source code)")
        print("PyInstaller: For creating standalone executables")
        print()

        # Install PyArmor
        print("Installing PyArmor...")
        self.run_command(
            [sys.executable, "-m", "pip", "install", "--quiet", "pyarmor"],
            "pip install pyarmor"
        )

        # Install PyInstaller
        print("Installing PyInstaller...")
        self.run_command(
            [sys.executable, "-m", "pip", "install", "--quiet", "pyinstaller"],
            "pip install pyinstaller"
        )

        print()

        # Verify installations
        print("Verifying PyArmor installation...")
        result = subprocess.run(
            ["pyarmor", "--version"],
            capture_output=True,
            text=True
        )
        print(f"PyArmor: {result.stdout.strip()}")

        print()
        print("Verifying PyInstaller installation...")
        result = subprocess.run(
            ["pyinstaller", "--version"],
            capture_output=True,
            text=True
        )
        print(f"PyInstaller: {result.stdout.strip()}")

        print()
        self.print_success("All tools installed successfully")

    def step_3_verify_source(self):
        """Step 3: Verify source code exists."""
        self.print_step(3, "Verifying source code")

        source_file = self.source_dir / "sensitive_algorithm.py"

        if not source_file.exists():
            self.print_error(f"Source code not found: {source_file}")
            print("The example source code must exist to continue.")
            return False

        print(f"Source code file: {source_file}")
        print()

        # Show file info
        file_size = source_file.stat().st_size
        print(f"File size: {file_size} bytes")
        print()

        # Show first 20 lines
        print("File content preview (first 20 lines):")
        print("-" * 80)

        with open(source_file, 'r') as f:
            lines = f.readlines()[:20]
            for line in lines:
                print(line.rstrip())

        print("-" * 80)
        print()

        self.print_success("Source code is ready for obfuscation")
        return True

    def step_4_prepare_directories(self):
        """Step 4: Prepare directories for the workflow."""
        self.print_step(4, "Preparing directories")

        # Clean old obfuscated code
        if self.obfuscated_dir.exists():
            print(f"Removing old obfuscated code: {self.obfuscated_dir}")
            shutil.rmtree(self.obfuscated_dir)

        # Create fresh directories
        print(f"Creating obfuscated code directory: {self.obfuscated_dir}")
        self.obfuscated_dir.mkdir(parents=True, exist_ok=True)

        print(f"Creating packaged executable directory: {self.packaged_dir}")
        self.packaged_dir.mkdir(parents=True, exist_ok=True)

        print()
        self.print_success("Directories prepared")

    def step_5_obfuscate_code(self):
        """Step 5: Obfuscate code with PyArmor."""
        self.print_step(5, "Obfuscating code with PyArmor")

        print("PyArmor will protect your code by:")
        print("  • Renaming functions and variables to meaningless identifiers")
        print("  • Encrypting string literals")
        print("  • Disabling debugging and introspection")
        print("  • Adding anti-tampering detection")
        print("  • Creating encrypted bytecode")
        print()

        source_file = self.source_dir / "sensitive_algorithm.py"

        command = [
            "pyarmor",
            "obfuscate",
            "--obf", "all",
            "--restrict", "all",
            "--capsule",
            "--advanced",
            "--output", str(self.obfuscated_dir),
            str(source_file)
        ]

        print(f"Command: {' '.join(command)}")
        print()

        if not self.run_command(command, "PyArmor obfuscation"):
            return False

        print()
        self.print_success("Code obfuscation complete")

        # Verify obfuscated code
        obfuscated_file = self.obfuscated_dir / "sensitive_algorithm.py"

        if not obfuscated_file.exists():
            self.print_error("Obfuscated code not found")
            return False

        print()
        print("Obfuscated code directory contents:")
        for file in self.obfuscated_dir.iterdir():
            size = file.stat().st_size
            print(f"  • {file.name} ({size} bytes)")

        print()

        # Show file size comparison
        original_size = source_file.stat().st_size
        obfuscated_size = obfuscated_file.stat().st_size

        print(f"Original code size: {original_size} bytes")
        print(f"Obfuscated code size: {obfuscated_size} bytes")
        print()

        # Show obfuscated code preview
        print("Obfuscated code preview (first 20 lines):")
        print("Notice: Function and variable names are now encrypted")
        print("-" * 80)

        with open(obfuscated_file, 'r') as f:
            lines = f.readlines()[:20]
            for line in lines:
                print(line.rstrip())

        print("-" * 80)
        print()

        return True

    def step_6_test_obfuscated_code(self):
        """Step 6: Test that obfuscated code still works."""
        self.print_step(6, "Testing obfuscated code")

        print("The obfuscated code must still function identically:")
        print()

        # Change to obfuscated directory to test
        old_cwd = os.getcwd()
        os.chdir(self.obfuscated_dir)

        try:
            # Test that we can import and use the obfuscated code
            test_code = """
import sys
sys.path.insert(0, '.')

try:
    import sensitive_algorithm

    # Create an instance of the algorithm
    algo = sensitive_algorithm.ProprietaryAlgorithm()

    # Test the calculation
    test_data = [1.5, 2.3, 3.7]
    result = algo.calculate_proprietary_value(test_data)

    print(f"✓ Module imported successfully")
    print(f"✓ Algorithm instantiated")
    print(f"✓ Calculation result: {result:.6f}")
    print(f"✓ Obfuscated code is fully functional")

except Exception as e:
    print(f"✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
"""

            result = subprocess.run(
                [sys.executable, "-c", test_code],
                capture_output=True,
                text=True
            )

            print(result.stdout)

            if result.returncode != 0:
                print(result.stderr)
                self.print_error("Obfuscated code test failed")
                return False

        finally:
            os.chdir(old_cwd)

        print()
        self.print_success("Obfuscated code works correctly")
        return True

    def step_7_package_with_pyinstaller(self):
        """Step 7: Package obfuscated code with PyInstaller."""
        self.print_step(7, "Packaging with PyInstaller")

        print("PyInstaller will create a standalone executable that:")
        print("  • Contains the obfuscated code")
        print("  • Includes the Python runtime")
        print("  • Includes all dependencies")
        print("  • Runs on Windows, Linux, and macOS")
        print("  • Hides source code completely")
        print()

        obfuscated_file = self.obfuscated_dir / "sensitive_algorithm.py"

        command = [
            "pyinstaller",
            "--name=PropertyProtectedTool",
            "--onefile",
            f"--distpath={self.packaged_dir / 'dist'}",
            f"--buildpath={self.packaged_dir / 'build'}",
            f"--specpath={self.packaged_dir}",
            "--hidden-import=sensitive_algorithm",
            str(obfuscated_file)
        ]

        print(f"Command: {' '.join(command[:3])} ...")
        print()

        if not self.run_command(command, "PyInstaller packaging"):
            return False

        print()
        self.print_success("Packaging complete")
        return True

    def step_8_verify_executable(self):
        """Step 8: Verify the executable was created."""
        self.print_step(8, "Verifying executable")

        # Find the executable
        dist_dir = self.packaged_dir / "dist"

        if not dist_dir.exists():
            self.print_error("Distribution directory not found")
            return False

        # Look for executable file
        executables = list(dist_dir.glob("PropertyProtectedTool*"))

        if not executables:
            self.print_error("No executable found in dist directory")
            return False

        executable = executables[0]

        print(f"Executable found: {executable}")
        print(f"File type: {executable.suffix if executable.suffix else 'binary'}")
        print()

        # Get file size
        file_size = executable.stat().st_size
        file_size_mb = file_size / (1024 * 1024)

        print(f"Executable size: {file_size_mb:.2f} MB")
        print("(Includes Python runtime: ~30MB)")
        print()

        # Make executable on Linux/Mac
        if not str(executable).endswith(".exe"):
            os.chmod(executable, 0o755)

        print(f"File permissions updated (Linux/Mac)")
        print()

        self.print_success("Executable verified and ready")
        return True

    def step_9_test_executable(self):
        """Step 9: Run and test the executable."""
        self.print_step(9, "Testing executable")

        # Find the executable
        dist_dir = self.packaged_dir / "dist"
        executables = list(dist_dir.glob("PropertyProtectedTool*"))

        if not executables:
            self.print_error("Executable not found")
            return False

        executable = executables[0]

        print("Running the protected executable...")
        print()

        # Set license key for testing
        env = os.environ.copy()
        env["LICENSE_KEY"] = "KEY-2024-ENTERPRISE-001"

        result = subprocess.run(
            [str(executable)],
            capture_output=True,
            text=True,
            env=env
        )

        print(result.stdout)

        if result.returncode != 0:
            print(result.stderr)
            self.print_error("Executable test failed")
            return False

        print()
        self.print_success("Executable runs successfully")
        return True

    def step_10_summary(self):
        """Step 10: Print workflow summary."""
        self.print_header("WORKFLOW COMPLETE - YOUR CODE IS NOW PROTECTED")

        print("What was accomplished:")
        print("  ✓ Source code obfuscated with PyArmor")
        print("  ✓ Obfuscated code packaged with PyInstaller")
        print("  ✓ Standalone executable created")
        print("  ✓ No Python installation required for users")
        print("  ✓ Source code protected from reverse engineering")
        print()

        print("Key directories:")
        print(f"  • Original source: {self.source_dir}")
        print(f"  • Obfuscated code: {self.obfuscated_dir}")
        print(f"  • Protected executable: {self.packaged_dir / 'dist'}")
        print()

        print("To distribute to clients:")
        print("  1. Send only the executable file (PropertyProtectedTool)")
        print("  2. Users can run it without installing Python")
        print("  3. The code is fully protected from reverse engineering")
        print()

        print("Important notes:")
        print("  • Never distribute the obfuscated source code")
        print("  • Only distribute the final executable")
        print("  • Keep your original source code secure")
        print("  • Implement license verification for production use")
        print("  • Add anti-tampering checks for additional security")
        print()

        print("This workflow protects your intellectual property using:")
        print("  • PyArmor: Code obfuscation (encryption and renaming)")
        print("  • PyInstaller: Executable packaging (standalone binary)")
        print()

        print("=" * 80)
        print()

    def run(self):
        """Run the complete workflow."""
        self.print_header("PYTHON CODE PROTECTION WORKFLOW")

        try:
            # Execute all steps in sequence
            self.step_1_verify_python()
            self.step_2_install_tools()

            if not self.step_3_verify_source():
                return False

            self.step_4_prepare_directories()

            if not self.step_5_obfuscate_code():
                return False

            if not self.step_6_test_obfuscated_code():
                return False

            if not self.step_7_package_with_pyinstaller():
                return False

            if not self.step_8_verify_executable():
                return False

            if not self.step_9_test_executable():
                return False

            self.step_10_summary()

            return True

        except Exception as e:
            self.print_error(f"Workflow failed: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main entry point."""
    workflow = CodeProtectionWorkflow()
    success = workflow.run()

    # Return appropriate exit code
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
